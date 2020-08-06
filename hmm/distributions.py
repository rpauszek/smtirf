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

    def __init__(self, alpha):
        self._alpha = alpha
        self._isStack = alpha.ndim > 1

    @property
    def alpha(self):
        return self._alpha

    @property
    def alpha0(self):
        if self._isStack:
            return np.sum(self._alpha, axis=1)
        else:
            return np.sum(self._alpha)

    @property
    def mu(self):
        return normalize_rows(self._alpha)

    @property
    def lnMuStar(self):
        return digamma(self.alpha) - col(digamma(self.alpha0))

    def sample(self):
        if self._isStack:
            return np.vstack([np.random.dirichlet(ak) for ak in self.alpha])
        else:
            return np.random.dirichlet(self.alpha)


# class DirichletArray(Dirichlet):
#
#     @property
#     def alpha0(self):
#         return np.sum(self._alpha, axis=1)


class Normal():

    def __init__(self):
        pass


class NormalSharedVariance():

    def __init__(self):
        pass


class NormalGamma():

    def __init__(self):
        pass


class NormalGammaSharedVariance():

    def __init__(self):
        pass
