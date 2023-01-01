import numpy as np
from dataclasses import dataclass
from sklearn.cluster import KMeans
from . import row, col
from ..util import AsDictMixin


@dataclass(frozen=True)
class Categorical(AsDictMixin):
    """Categorical distribution: Cat(x|μ)."""

    K: int
    mu: np.ndarray

    @classmethod
    def initialize_vector(cls, K):
        return cls(K, np.ones((1, K)) / K)

    @classmethod
    def initalize_array(cls, K, *, self_transition=0):
        diagonal = np.eye(K) * (self_transition - 1)

        return cls(K, diagonal + np.ones((K, K)))._normalize()

    def _normalize(self):
        norm_factor = col(self.mu.sum(axis=1))
        return Categorical(self.K, self.mu / norm_factor)

    def update(self, p):
        return Categorical(self.K, p)


@dataclass(frozen=True)
class Normal(AsDictMixin):
    """Normal distribution: N(x|μ,τ)."""

    K: int
    mu: np.ndarray
    tau: np.ndarray or float

    @classmethod
    def initialize_kmeans(cls, K, x, shared_variance):
        model = KMeans(n_clusters=K)
        labels = model.fit_predict(col(x))

        mu = model.cluster_centers_.squeeze()
        idx = np.argsort(mu)

        x0 = x - mu[labels]
        std = (
            np.array([np.std(x0)])
            if shared_variance
            else np.array([np.std(x0[labels == j]) for j in np.unique(labels)])[idx]
        )

        return cls(K, mu[idx], 1 / std**2)

    @property
    def var(self):
        return 1 / self.tau

    @property
    def sigma(self):
        return np.sqrt(1 / self.tau)

    def pdf(self, x):
        """Evaluate the probability density function P(x|μ,τ) for all values of x."""

        # work in log space to avoid over/underflow
        x2 = (row(x) - col(self.mu)) ** 2
        tau = col(self.tau)
        log_p = -0.5 * (np.log(2 * np.pi) - np.log(tau) + x2 * tau)
        return np.exp(log_p)

    @staticmethod
    def _calc_sufficient_statistics(x, gamma):
        N_k = gamma.sum(axis=0)
        x_bar = np.sum(gamma * col(x), axis=0) / N_k
        variance = np.sum(gamma * (col(x) - row(x_bar)) ** 2, axis=0) / N_k
        return N_k, x_bar, variance

    def update(self, x, gamma):
        N_k, x_bar, variance = self._calc_sufficient_statistics(x, gamma)

        # shared variance
        # un-normalize variance, sum, re-normalize
        if len(self.tau) == 1:
            variance = np.array([np.sum(variance * N_k) / N_k.sum()])

        return Normal(self.K, x_bar, 1 / variance)
