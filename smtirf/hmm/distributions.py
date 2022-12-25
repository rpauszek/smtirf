import numpy as np
from dataclasses import dataclass
from sklearn.cluster import KMeans
from . import row, col


@dataclass(frozen=True)
class Categorical:
    """Categorical distribution: Cat(x|μ)."""

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

    def update(self, p):
        return Categorical(self.K, p)


@dataclass(frozen=True)
class Normal:
    """Normal distribution: N(x|μ,τ)."""

    K: int
    mu: np.ndarray
    tau: np.ndarray or float

    @classmethod
    def initialize_kmeans(cls, K, x):
        model = KMeans(n_clusters=K)
        labels = model.fit_predict(col(x))

        mu = model.cluster_centers_.squeeze()
        x0 = x - mu[labels]
        std = np.array([np.std(x0[labels == j]) for j in np.unique(labels)])

        idx = np.argsort(mu)
        return cls(K, mu[idx], 1 / std[idx] ** 2)

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
    def calc_sufficient_statistics(x, gamma):
        Nk = gamma.sum(axis=0)
        xbar = np.sum(gamma * col(x), axis=0) / Nk
        S = np.sum(gamma * (col(x) - row(xbar)) ** 2, axis=0) / Nk  # variance
        return Nk, xbar, S

    def update(self, x, gamma):
        Nk, xbar, S = self.calc_sufficient_statistics(x, gamma)
        return Normal(self.K, xbar, 1 / S)
