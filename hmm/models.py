# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> hmm >> models
"""
import numpy as np
from . import row, col, normalize_rows
from . import algorithms as hmmalg
from .distributions import *

# ==============================================================================
# BASE MODEL CLASS
# ==============================================================================
class BaseHiddenMarkovModel():

    def simulate(self, M=1, T=1000):
        """ simulate M traces of length T from model """
        S = [hmmalg.sample_statepath(self.K, self.pi, self.A, T=T) for m in range(M)]
        Y = [np.random.normal(loc=self.mu[s], scale=self.sigma[s]) for s in S]
        return [(s, y) for s, y in zip(S,Y)]


# ==============================================================================
# CONCRETE MODEL SUBCLASSES
# ==============================================================================
class ClassicHiddenMarkovModel(BaseHiddenMarkovModel):

    def __init__(self, K, pi, A, mu, tau, sharedVariance):
        self._K = K
        self._pi = Categorical(pi)
        self._A = CategoricalArray(A)
        if sharedVariance:
            self._phi = NormalSharedVariance(mu, tau)
        else:
            self._phi = Normal(mu, tau)
        assert self._pi.K == K and self._A.K == K and self._phi.K == K
        self.sharedVariance = sharedVariance
        self.exitFlag = None

    @property
    def K(self):
        return self._K

    @property
    def pi(self):
        return self._pi.mu

    @property
    def A(self):
        return self._A.mu

    @property
    def mu(self):
        return self._phi.mu

    @property
    def sigma(self):
        return self._phi.sigma

    def p_X(self, x):
        return self._phi.p_X(x)

    def update(self, x, gamma, xi):
        self._pi.update(gamma[0])
        self._A.update(xi/col(gamma[:-1].sum(axis=0)))
        self._phi.update(x, gamma)

    def train(self, x, maxIter=1000, tol=1e-5, printWarnings=True):
        self.exitFlag = hmmalg.train_baumwelch(x, self, maxIter=maxIter, tol=tol, printWarnings=printWarnings)

    @classmethod
    def train_new(cls, x, K, sharedVariance, maxIter=1000, tol=1e-5, printWarnings=True):
        # initial guess for parameters
        pi = np.ones(K)/K
        A = normalize_rows(np.eye(K)*1 + np.ones((K,K)))
        mu = np.linspace(0, 1, K+2)[1:-1]
        if sharedVariance:
            sigma = 0.1
        else:
            sigma = np.ones(K)*0.1
        theta = cls(K, pi, A, mu, 1/sigma**2, sharedVariance)
        # TRAIN
        theta.train(x)
        return theta



class VariationalHiddenMarkovModel(BaseHiddenMarkovModel):

    def __init__(self, K, u, w, sharedVariance):
        self._K = K
        self._u = u
        self._w = w
        assert self._u.K == K and self.w.K == K
        self.sharedVariance = sharedVariance
        self.exitFlag = None

    @property
    def K(self):
        return self._K

    @property
    def pi(self):
        return self._w.pi

    @property
    def A(self):
        return self._w.A

    @property
    def mu(self):
        return self._w.mu

    @property
    def sigma(self):
        return self._w.sigma

    def p_X(self, x):
        return self._w.p_X(x)


# ==============================================================================
# MODEL FACTORY CLASS
# ==============================================================================
class HiddenMarkovModel():

    # _MODEL_TYPES = {"em" : (models.ClassicHiddenMarkovModel, svmodels.ClassicHiddenMarkovModelSharedVariance),
    #                 "vb" : (models.BayesianHiddenMarkovModel, svmodels.BayesianHiddenMarkovModelSharedVariance),
    #                 "piecewise" : (models.PiecewiseHiddenMarkovModel, svmodels.PiecewiseHiddenMarkovModelSharedVariance),
    #                 "multimer" : (None, svmodels.MultimerHiddenMarkovModel)}

    # ==========================================================================
    # initializers
    # ==========================================================================
    @staticmethod
    def new(K, modelType="em", sharedVariance=True, maxIter=1000, tol=1e-5):
        pass
