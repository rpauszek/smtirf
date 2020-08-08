# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> hmm >> distributions
"""
import numpy as np
from numpy import AxisError
from scipy.special import gammaln, digamma
from . import row, col, normalize_rows

__all__ = ["Categorical", "CategoricalArray",
           "Dirichlet", "DirichletArray",
           "Normal", "NormalSharedVariance",
           "NormalGamma", "NormalGammaSharedVariance"]

class Categorical():
    _NDIM = 1

    def __init__(self, mu):
        assert mu.ndim == self._NDIM
        if self._NDIM == 1:
            assert np.sum(mu) == 1
        elif self._NDIM == 2:
            assert np.all(np.sum(mu, axis=1) == 1)
        self._mu = mu

    @property
    def K(self):
        return self.mu.size

    @property
    def mu(self):
        return self._mu

    def update(self, p):
        self._mu = p


class CategoricalArray(Categorical):
    _NDIM = 2

    @property
    def K(self):
        _, K = self.mu.shape
        return K


class Dirichlet():
    _NDIM = 1

    def __init__(self, alpha):
        assert alpha.ndim == self._NDIM
        self._alpha = alpha

    @property
    def K(self):
        return self.alpha.size

    @property
    def alpha(self):
        return self._alpha

    @property
    def alpha0(self):
        return np.sum(self._alpha)

    @property
    def mu(self):
        return normalize_rows(self.alpha)

    @property
    def lnMuStar(self):
        return digamma(self.alpha) - col(digamma(self.alpha0))

    def sample(self):
        return np.random.dirichlet(self.alpha)


class DirichletArray(Dirichlet):
    _NDIM = 2

    @property
    def K(self):
        _, K = self.alpha.shape
        return K

    @property
    def alpha0(self):
        return np.sum(self._alpha, axis=1)

    def sample(self):
        return np.vstack([np.random.dirichlet(ak) for ak in self.alpha])


class Normal():
    """ N(x|μ,τ) """

    def __init__(self, mu, tau):
        assert mu.ndim == 1
        assert tau.ndim == 1
        self._mu = mu
        self._tau = tau

    @property
    def K(self):
        return self._mu.size

    @property
    def mu(self):
        return self._mu

    @property
    def tau(self):
        return self._tau

    @property
    def var(self):
        return 1/self.tau

    @property
    def sigma(self):
        return np.sqrt(1/self.tau)

    def p_X(self, x):
        """ P(x|μ,τ) """
        X = row(x) - col(self.mu)
        lnP = -0.5 * np.log(2*np.pi/col(self.tau)) - col(self.tau)/2 * X**2
        return np.exp(lnP)

    @staticmethod
    def calc_sufficient_statistics(x, gamma):
        Nk = gamma.sum(axis=0)
        xbar = np.sum(gamma*col(x), axis=0)/Nk
        S = np.sum(gamma*(col(x)-row(xbar))**2, axis=0)/Nk # variance
        return Nk, xbar, S

    def update(self, x, gamma):
        Nk, xbar, S = self.calc_sufficient_statistics(x, gamma)
        self._mu = xbar
        self._tau = 1/S


class NormalSharedVariance(Normal):

    def __init__(self, mu, tau):
        assert mu.ndim == 1
        assert not isinstance(tau, (np.ndarray, list, tuple))
        self._mu = mu
        self._tau = tau

    def update(self, x, gamma):
        Nk, xbar, S = self.calc_sufficient_statistics(x, gamma)
        self._mu = xbar
        self._tau = 1/((S*Nk).sum()/Nk.sum()) # un-normalize S, sum, re-normalize

    # @property
    # def tau(self):
    #     return np.full(self.K, self._tau)


class NormalGamma(Normal):
    """ NG(μ,τ|m,β,a,b) """

    def __init__(self, m, beta, a, b):
        assert m.ndim == 1 and beta.ndim == 1
        assert a.ndim == 1 and b.ndim == 1
        self._m = m
        self._beta = beta
        self._a = a
        self._b = b

    @property
    def K(self):
        return self._m.size

    @property
    def m(self):
        return self._m

    @property
    def beta(self):
        return self._beta

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def mu(self):
        return self._m

    @property
    def tau(self):
        return self.a/self.b

    def p_mu(self, m):
        """ P(μ|m,βτ) """
        X = row(m) - col(self.m)
        tau = col(self.beta * self.tau)
        lnP = -0.5 * np.log(2*np.pi/tau) - tau/2 * X**2
        return np.exp(lnP)

    def p_tau(self, t):
        """ P(τ|a,b) """
        t = row(t)
        lnP = -gammaln(col(self.a)) + col(self.a*np.log(self.b)) + col(self.a-1)*np.log(t) - col(self.b)*t
        return np.exp(lnP)

    @property
    def lnTauStar(self):
        return digamma(self.a) - np.log(self.b)

    def mahalanobis(self, x):
        Delta2 = row(1/self.beta) + row(self.tau)*(col(x)-row(self.m))**2
        return 0.5*row(self.lnTauStar) - 0.5*np.log(2*np.pi) - 0.5*Delta2

    def sample(self):
        sigma = np.sqrt(1/(self.beta*self.tau))
        mu = np.sort(np.random.normal(loc=self.m, scale=sigma))
        tau = np.random.gamma(shape=self.a, scale=1/self.b)
        return mu, tau


class NormalGammaSharedVariance(NormalGamma):

    def __init__(self, m, beta, a, b):
        assert m.ndim == 1 and beta.ndim == 1
        assert not isinstance(a, (np.ndarray, list, tuple))
        assert not isinstance(b, (np.ndarray, list, tuple))
        self._m = m
        self._beta = beta
        self._a = a
        self._b = b
