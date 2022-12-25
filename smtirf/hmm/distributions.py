import numpy as np
from dataclasses import dataclass
from . import col


@dataclass(frozen=True)
class Categorical:
    K: int
    mu: np.ndarray

    @classmethod
    def initialize_vector(cls, K):
        return cls(K, np.ones((1, K)) / K)

    @classmethod
    def initalize_array(cls, K, *, self_transition=0):
        diagonal = np.eye(K) * (self_transition - 1)

        return cls(K, diagonal + np.ones((K, K))).normalize()

    def normalize(self):
        norm_factor = col(self.mu.sum(axis=1))
        return Categorical(self.K, self.mu / norm_factor)
