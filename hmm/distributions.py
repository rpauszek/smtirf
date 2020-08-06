# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> hmm >> distributions
"""
import numpy as np
from numpy import AxisError
from scipy.special import gammaln, digamma
from . import row, col, normalize_rows

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


class NormalSharedVariance(Normal):

    def __init__(self, mu, tau):
        assert mu.ndim == 1
        assert not isinstance(tau, (np.ndarray, list, tuple))
        self._mu = mu
        self._tau = tau

    # @property
    # def tau(self):
    #     return np.full(self.K, self._tau)


class NormalGamma():

    def __init__(self):
        pass


class NormalGammaSharedVariance():

    def __init__(self):
        pass
