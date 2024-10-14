import abc


class Querier(abc.ABC):

    def __init__(self):
        self.finished_cluster = False
        pass

    @abc.abstractmethod
    def query_points(self, idx1, idx2):
        return

    def continue_cluster_process(self):
        return True

    def update_clustering(self, clustering):
        pass

    def update_clustering_detailed(self, clustering):
        pass
