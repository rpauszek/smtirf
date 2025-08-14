# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> hmm >> __init__.py
"""
import numpy as np
from numpy.exceptions import AxisError


def row(x):
    try:
        return x[np.newaxis,:]
    except IndexError:
        return x
    except TypeError:
        return x

def col(x):
    try:
        return x[:,np.newaxis]
    except IndexError:
        return x
    except TypeError:
        return x

def normalize_rows(x):
    try:
        return x/col(x.sum(axis=1))
    except AxisError:
        return x/x.sum()
    except AttributeError:
        return normalize_rows(np.array(x))

class ExitFlag():

    def __init__(self, L, isConverged):
        self.L = L
        self.isConverged = isConverged

    def _as_dict(self):
        return {"L": self.L, "isConverged": self.isConverged}

    def __str__(self):
        s = f"\nTraining Summary:\nlog(L):\t{self.Lmax:0.2f} (Δ={self.deltaL:0.2e})"
        s += f"\nIterations:\t{self.iterations}"
        s += f"\nConverged:\t{self.isConverged}\n"
        return s

    @property
    def iterations(self):
        return self.L.size

    @property
    def deltaL(self):
        return self.L[-1] - self.L[-2]

    @property
    def Lmax(self):
        return self.L[-1]


from . import hyperparameters
from . import models
from .models import HiddenMarkovModel
