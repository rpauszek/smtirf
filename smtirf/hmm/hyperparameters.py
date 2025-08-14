import numpy as np
import copy
from . import row
from .distributions import *


class HMMHyperParameters:

    def __init__(self, K, rho, alpha, m, beta, a, b):
        self._K = K
        self._rho = Dirichlet(rho)
        self._alpha = DirichletArray(alpha)
        self._phi = NormalGamma(m, beta, a, b)

    def _as_dict(self):
        return {
            "K": self.K,
            "rho": self._rho.alpha,
            "alpha": self._alpha.alpha,
            "m": self._phi.m,
            "beta": self._phi.beta,
            "a": self._phi.a,
            "b": self._phi.b,
        }

    @classmethod
    def uninformative(cls, K, rho0=1, alpha0_ii=1, m0=0.5, beta0=0.25, a0=2.5, b0=0.1):
        rho = np.ones(K) * rho0
        alpha = np.eye(K) * alpha0_ii + np.ones((K, K))
        m = np.ones(K) * m0
        beta = np.ones(K) * beta0
        a = np.ones(K) * a0
        b = np.ones(K) * b0
        return cls(K, rho, alpha, m, beta, a, b)

    def draw_parameter_sample(self):
        pi = self._rho.sample()
        A = self._alpha.sample()
        mu, tau = self._phi.sample()
        return pi, A, mu, tau

    def sample_posterior(self, T=1000):
        gamma0, xiSum, xbar, tau = self.draw_parameter_sample()
        gamma0 = row(gamma0)
        S = 1 / tau  # precision -> variance
        Nk = np.ones(self.K) * T / self.K
        w = copy.deepcopy(self)
        w.update(self, gamma0 * T, xiSum * T, Nk, xbar, S)
        w.sort()
        return w

    @property
    def K(self):
        return self._K

    @property
    def pi(self):
        return self._rho.mu

    @property
    def A(self):
        return self._alpha.mu

    @property
    def mu(self):
        return self._phi.mu

    @property
    def sigma(self):
        return self._phi.sigma

    @property
    def lnPiStar(self):
        return self._rho.lnMuStar

    @property
    def lnAStar(self):
        return self._alpha.lnMuStar

    def mahalanobis(self, x):
        return self._phi.mahalanobis(x)

    def p_X(self, x):
        return self._phi.p_X(x)

    def update(self, u, gamma, xiSum, Nk, xbar, S):
        self._rho.update(u._rho, gamma[0])
        self._alpha.update(u._alpha, xiSum)
        self._phi.update(u._phi, Nk, xbar, S)

    def sort(self):
        ix = np.argsort(self.mu)
        self._rho.reorder(ix)
        self._alpha.reorder(ix)
        self._phi.reorder(ix)

    def refine_by_kmeans(self, x, u):
        self._phi.refine_by_kmeans(x, u)


class HMMHyperParametersSharedVariance(HMMHyperParameters):

    def __init__(self, K, rho, alpha, m, beta, a, b):
        self._K = K
        self._rho = Dirichlet(rho)
        self._alpha = DirichletArray(alpha)
        self._phi = NormalGammaSharedVariance(m, beta, a, b)

    @classmethod
    def uninformative(cls, K, rho0=1, alpha0_ii=1, m0=0.5, beta0=0.25, a0=2.5, b0=0.01):
        rho = np.ones(K) * rho0
        alpha = np.eye(K) * alpha0_ii + np.ones((K, K))
        m = np.ones(K) * m0
        beta = np.ones(K) * beta0
        a = a0
        b = b0
        return cls(K, rho, alpha, m, beta, a, b)


class HmmHyperParametersMultimer(HMMHyperParametersSharedVariance):

    def __init__(self, K, rho, alpha, d0, epsilon, m0, beta, a, b):
        self._K = K
        self._rho = Dirichlet(rho)
        self._alpha = DirichletArray(alpha)
        self._phi = MultimerNormalGamma(K, d0, epsilon, m0, beta, a, b)

    def _as_dict(self):
        return {
            "K": self.K,
            "rho": self._rho.alpha,
            "alpha": self._alpha.alpha,
            "d0": self._phi.d0,
            "epsilon": self._phi.epsilon,
            "m0": self._phi.m0,
            "beta": self._phi.beta,
            "a": self._phi.a,
            "b": self._phi.b,
        }

    @classmethod
    def uninformative(
        cls,
        K,
        rho0=1,
        alpha0_ii=1,
        d0=20,
        epsilon0=0.25,
        m0=250,
        beta0=0.25,
        a0=10,
        b0=25000,
    ):
        rho = np.ones(K) * rho0
        alpha = np.eye(K) * alpha0_ii + np.ones((K, K))
        return cls(K, rho, alpha, d0, epsilon0, m0, beta0, a0, b0)

    @property
    def delta(self):
        return self._phi.d0

    @property
    def mu0(self):
        return self._phi.m0

    @property
    def mu(self):
        return self._phi.mu

    def draw_parameter_sample(self):
        pi = self._rho.sample()
        A = self._alpha.sample()
        delta, mu0, tau = self._phi.sample()
        return pi, A, delta, mu0, tau

    def sample_posterior(self, T=1000):
        gamma0, xiSum, dbar, xbar, tau = self.draw_parameter_sample()
        gamma0 = row(gamma0)
        S = 1 / tau  # precision -> variance
        Nk = np.ones(self.K) * T / self.K
        w = copy.deepcopy(self)
        w.update(self, gamma0 * T, xiSum * T, Nk, dbar, xbar, S)
        # w.sort()
        return w

    def update(self, u, gamma, xiSum, Nk, dbar, xbar, S):
        self._rho.update(u._rho, gamma[0])
        self._alpha.update(u._alpha, xiSum)
        self._phi.update(u._phi, Nk, dbar, xbar, S)
