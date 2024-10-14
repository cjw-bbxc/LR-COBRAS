import abc
import itertools
import sys
import time
import copy

import numpy as np
import requests

from cobras_ts.cluster import Cluster

from cobras_ts.clustering import Clustering
from prolog.PrologUtils import PrologUtils


class COBRAS(abc.ABC):
    def __init__(self, data, querier, max_questions, train_indices=None, store_intermediate_results=True, queries=0):

        self.data = data
        self.querier = querier
        self.max_questions = max_questions
        self.store_intermediate_results = store_intermediate_results

        if train_indices is None:
            self.train_indices = range(self.data.shape[0])
        else:
            self.train_indices = train_indices

        self.clustering = None
        self.split_cache = dict()
        self.start_time = None
        self.intermediate_results = []
        self.ml = None
        self.cl = None
        self.prolog = PrologUtils

    def cluster(self):

        self.start_time = time.time()

        
        
        initial_superinstance = self.create_superinstance(list(range(self.data.shape[0])))

        
        self.ml = []
        self.cl = []

        self.clustering = Clustering([Cluster([initial_superinstance])])

        
        
        initial_k = self.determine_split_level(initial_superinstance,
                                               copy.deepcopy(self.clustering.construct_cluster_labeling()))

        
        superinstances = self.split_superinstance(initial_superinstance, initial_k)
        self.clustering.clusters = []
        for si in superinstances:
            self.clustering.clusters.append(Cluster([si]))

        
        
        self.merge_containing_clusters(copy.deepcopy(self.clustering.construct_cluster_labeling()))
        last_valid_clustering = copy.deepcopy(self.clustering)

        
        while len(self.ml) + len(self.cl) < self.max_questions:
            
            self.querier.update_clustering(self.clustering)

            
            
            
            if not self.querier.continue_cluster_process():
                break

            
            to_split, originating_cluster = self.identify_superinstance_to_split()
            if to_split is None:
                break

            
            clustering_to_store = None
            if self.intermediate_results:
                clustering_to_store = self.clustering.construct_cluster_labeling()

            
            originating_cluster.super_instances.remove(to_split)
            if len(originating_cluster.super_instances) == 0:
                self.clustering.clusters.remove(originating_cluster)

            
            
            split_level = self.determine_split_level(to_split, clustering_to_store)

            
            new_super_instances = self.split_superinstance(to_split, split_level)

            
            new_clusters = self.add_new_clusters_from_split(new_super_instances)
            if not new_clusters:
                
                
                
                
                
                
                originating_cluster.super_instances.append(to_split)
                to_split.tried_splitting = True
                to_split.children = None

                if originating_cluster not in self.clustering.clusters:
                    self.clustering.clusters.append(originating_cluster)

                continue
            else:
                self.clustering.clusters.extend(new_clusters)

            
            fully_merged = self.merge_containing_clusters(clustering_to_store)
            
            
            if fully_merged:
                last_valid_clustering = copy.deepcopy(self.clustering)

        
        
        self.clustering = last_valid_clustering

        
        if self.store_intermediate_results:
            return self.clustering, [clust for clust, _, _ in self.intermediate_results], [runtime for _, runtime, _ in
                                                                                           self.intermediate_results], self.ml, self.cl
        else:
            return self.clustering

    @abc.abstractmethod
    def split_superinstance(self, si, k):

        return

    @abc.abstractmethod
    def create_superinstance(self, indices, parent=None):

        return

    def determine_split_level(self, superinstance, clustering_to_store):
        
        
        
        si = self.create_superinstance(superinstance.indices)

        must_link_found = False
        
        max_split = len(si.indices)
        split_level = 0

        while not must_link_found and len(self.ml) + len(self.cl) < self.max_questions:

            if len(si.indices) == 2:
                
                new_si = [self.create_superinstance([si.indices[0]]), self.create_superinstance([si.indices[1]])]
            else:
                
                
                new_si = self.split_superinstance(si, 2)

            if len(new_si) == 1:
                
                split_level = max([split_level, 1])
                split_n = 2 ** int(split_level)
                return min(max_split, split_n)

            s1 = new_si[0]
            s2 = new_si[1]
            
            
            pt1 = min([s1.representative_idx, s2.representative_idx])
            pt2 = max([s1.representative_idx, s2.representative_idx])

            
            if self.querier.query_points(pt1, pt2):
                
                self.ml.append((pt1, pt2))
                self.prolog.add_must_link(pt1, pt2)
                
                mls = self.prolog.valid_all_must_link()
                for m in mls:
                    if ((m['X'], m['Y']) not in self.ml) and ((m['Y'], m['X']) not in self.ml):
                        
                        self.ml.append((m['X'], m['Y']))
                
                confs = self.prolog.conflict_all_link()
                for c in confs:
                    
                    if (c['X'], c['Y']) in self.cl:
                        self.cl.remove((c['X'], c['Y']))
                    if (c['Y'], c['X']) in self.cl:
                        self.cl.remove((c['X'], c['Y']))
                    if (c['X'], c['Y']) in self.ml:
                        self.ml.remove((c['X'], c['Y']))
                    if (c['Y'], c['X']) in self.cl:
                        self.ml.remove((c['X'], c['Y']))
                    print('检测到冲突：', c)
                print('ml', self.ml)
                must_link_found = True
                if self.store_intermediate_results:
                    
                    self.intermediate_results.append(
                        (clustering_to_store, time.time() - self.start_time, len(self.ml) + len(self.cl)))
                continue
            else:
                
                self.cl.append((pt1, pt2))
                self.prolog.add_cannot_link(pt1, pt2)
                print('cl:', self.cl)
                
                split_level += 1
                if self.store_intermediate_results:
                    self.intermediate_results.append(
                        (clustering_to_store, time.time() - self.start_time, len(self.ml) + len(self.cl)))

            si_to_choose = []
            if len(s1.train_indices) >= 2:
                si_to_choose.append(s1)
            if len(s2.train_indices) >= 2:
                si_to_choose.append(s2)

            
            if len(si_to_choose) == 0:
                split_level = max([split_level, 1])
                split_n = 2 ** int(split_level)
                return min(max_split, split_n)

            
            
            si = min(si_to_choose, key=lambda x: len(x.indices))

        
        split_level = max([split_level, 1])
        split_n = 2 ** int(split_level)
        return min(max_split, split_n)

    def add_new_clusters_from_split(self, sis):
        
        new_clusters = []
        
        for x in sis:
            new_clusters.append(Cluster([x]))

        
        if len(new_clusters) == 1:
            return None
        else:
            return new_clusters

    def merge_containing_clusters(self, clustering_to_store):
        
        query_limit_reached = False
        merged = True
        
        while merged and len(self.ml) + len(self.cl) < self.max_questions:

            
            clusters_to_consider = [cluster for cluster in self.clustering.clusters if not cluster.is_finished]

            
            cluster_pairs = itertools.combinations(clusters_to_consider, 2)

            
            cluster_pairs = [x for x in cluster_pairs if
                             not x[0].cannot_link_to_other_cluster(x[1], self.cl)]

            
            cluster_pairs = sorted(cluster_pairs, key=lambda x: x[0].distance_to(x[1]))

            merged = False

            
            for x, y in cluster_pairs:

                
                if x.cannot_link_to_other_cluster(y, self.cl):
                    continue

                
                bc1, bc2 = x.get_comparison_points(y)
                pt1 = min([bc1.representative_idx, bc2.representative_idx])
                pt2 = max([bc1.representative_idx, bc2.representative_idx])

                
                
                if (pt1, pt2) in self.ml:
                    x.super_instances.extend(y.super_instances)
                    self.clustering.clusters.remove(y)
                    merged = True
                    break

                
                if len(self.ml) + len(self.cl) == self.max_questions:
                    query_limit_reached = True
                    break

                
                if self.querier.query_points(pt1, pt2):
                    x.super_instances.extend(y.super_instances)
                    self.clustering.clusters.remove(y)
                    self.ml.append((pt1, pt2))
                    
                    
                    

                    merged = True

                    if self.store_intermediate_results:
                        self.intermediate_results.append(
                            (clustering_to_store, time.time() - self.start_time, len(self.ml) + len(self.cl)))
                    break
                else:
                    self.cl.append((pt1, pt2))

                    if self.store_intermediate_results:
                        self.intermediate_results.append(
                            (clustering_to_store, time.time() - self.start_time, len(self.ml) + len(self.cl)))

        fully_merged = not query_limit_reached and not merged

        
        if fully_merged and self.store_intermediate_results:
            self.intermediate_results[-1] = (
                self.clustering.construct_cluster_labeling(), time.time() - self.start_time,
                len(self.ml) + len(self.cl))
        return fully_merged

    def identify_superinstance_to_split(self):
        

        
        if len(self.clustering.clusters) == 1 and len(self.clustering.clusters[0].super_instances) == 1:
            return self.clustering.clusters[0].super_instances[0], self.clustering.clusters[0]

        superinstance_to_split = None
        max_heur = -np.inf
        originating_cluster = None

        
        for cluster in self.clustering.clusters:

            
            if cluster.is_pure:
                continue

            
            if cluster.is_finished:
                continue

            for superinstance in cluster.super_instances:
                
                if superinstance.tried_splitting:
                    continue

                
                if len(superinstance.indices) == 1:
                    continue

                
                if len(superinstance.train_indices) < 2:
                    continue

                
                if len(superinstance.indices) > max_heur:
                    superinstance_to_split = superinstance
                    max_heur = len(superinstance.indices)
                    originating_cluster = cluster

        
        if superinstance_to_split is None:
            return None, None

        
        return superinstance_to_split, originating_cluster
