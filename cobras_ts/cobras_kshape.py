import numpy as np
from kshape.core import kshape, _sbd
from cobras_ts.superinstance_kshape import SuperInstance_kShape

from cobras_ts.cobras import COBRAS


class COBRAS_kShape(COBRAS):

    def split_superinstance(self, si, k):

        print(self.data.shape)
        pred = kshape(self.data[si.indices, :], k)

        training = []
        no_training = []

        for new_si_centroid, new_si_idx in pred:

            cur_indices = [si.indices[idx] for idx in new_si_idx]

            si_train_indices = [x for x in cur_indices if x in self.train_indices]
            if len(si_train_indices) != 0:
                training.append(SuperInstance_kShape(self.data, cur_indices, self.train_indices, new_si_centroid, si))
            else:
                no_training.append((cur_indices, new_si_centroid))

        for indices, centroid in no_training:

            closest_train = None
            closest_train_dist = np.inf
            for training_si in training:
                cur_dist, _ = _sbd(training_si.sbd_centroid, centroid)
                if cur_dist < closest_train_dist:
                    closest_train_dist = cur_dist
                    closest_train = training_si
            closest_train.indices.extend(indices)

        si.children = training

        return training

    def create_superinstance(self, indices, parent=None):
        return SuperInstance_kShape(self.data, indices, self.train_indices, parent)
