import numpy as np

from cobras_ts.superinstance import SuperInstance


def get_prototype(A, indices):
    max_affinity_to_others = -np.inf
    prototype_idx = None

    for idx in indices:
        affinity_to_others = 0.0
        for j in indices:
            if j == idx:
                continue
            affinity_to_others += A[idx, j]
        if affinity_to_others > max_affinity_to_others:
            prototype_idx = idx
            max_affinity_to_others = affinity_to_others

    return prototype_idx


class SuperInstance_DTW(SuperInstance):

    def __init__(self, data, indices, train_indices, parent=None):
        super(SuperInstance_DTW, self).__init__(data, indices, train_indices, parent)
        self.representative_idx = get_prototype(self.data, self.train_indices)

    def distance_to(self, other_superinstance):
        return -self.data[self.representative_idx, other_superinstance.representative_idx]
