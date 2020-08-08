# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> hmm >> hyperparameters
"""
import numpy as np
# from scipy.special import gammaln, digamma
import copy
from . import row, col
from .distributions import *


class HMMHyperParameters():

    def __init__(self, K, rho, alpha, m, beta, a, b):
        self._K = K
        self._rho = Dirichlet(rho)
        self._alpha = DirichletArray(alpha)
        self._phi = NormalGamma(m, beta, a, b)

    @classmethod
    def uninformative(cls, K, rho0=1, alpha0_ii=1, m0=0.5, beta0=0.25, a0=2.5, b0=0.1): #b0=0.01
        rho = np.ones(K) * rho0
        alpha = np.eye(K) * alpha0_ii + np.ones((K,K))
        m = np.ones(K) * m0
        beta = np.ones(K) * beta0
        a = np.ones(K)*a0
        b = np.ones(K)*b0
        return cls(K, rho, alpha, m, beta, a, b)

    def draw_parameter_sample(self):
        pi = self._rho.sample()
        A = self._alpha.sample()
        mu, tau = self._phi.sample() # convert to variance in return
        return pi, A, mu, 1/tau

    @staticmethod
    def sample_from_prior(u, T=1000):
        gamma0, xiSum, xbar, tau = u.draw_parameter_sample()
        gamma0 = row(gamma0)
        S = 1/tau
        Nk = np.ones(u.K) * T/u.K
        w = copy.deepcopy(u)
        w.update(u, gamma0*T, xiSum*T, Nk, xbar, S)
        w.sort()
        return w

    @property
    def K(self): return self._K

    @property
    def pi(self): return self._rho.mu

    @property
    def A(self): return self._alpha.mu

    @property
    def mu(self): return self._phi.mu

    @property
    def sigma(self): return self._phi.sigma

    def update(self, u, gamma, xiSum, Nk, xbar, S):
        self._rho.update(u._rho, gamma[0])
        self._alpha.update(u._alpha, xiSum)
        self._phi.update(u._phi, Nk, xbar, S)

    def sort(self):
        ix = np.argsort(self.mu)
        self._rho.reorder(ix)
        self._alpha.reorder(ix)
        self._phi.reorder(ix)



class HMMHyperParametersSharedVariance(HMMHyperParameters):

    def __init__(self, K, rho, alpha, m, beta, a, b):
        self._K = K
        self._rho = Dirichlet(rho)
        self._alpha = DirichletArray(alpha)
        self._phi = NormalGammaSharedVariance(m, beta, a, b)

    @classmethod
    def uninformative(cls, K, rho0=1, alpha0_ii=1, m0=0.5, beta0=0.25, a0=2.5, b0=0.01):
        rho = np.ones(K) * rho0
        alpha = np.eye(K) * alpha0_ii + np.ones((K,K))
        m = np.ones(K) * m0
        beta = np.ones(K) * beta0
        a = a0
        b = b0
        return cls(K, rho, alpha, m, beta, a, b)
