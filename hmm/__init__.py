# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> hmm >> __init__.py
"""
import numpy as np
from numpy import AxisError


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
