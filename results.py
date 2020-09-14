# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> results
"""
import numpy as np
from sklearn.neighbors import KernelDensity

import smtirf


class DwellTable():
    """ extracts a table of dwelltimes from trace fitted statepath
        dwells as rows, features as columns:
            start index | stop index | state | length | mu | xbar
        indices are for X attribute
    """

    def __init__(self, trc):
        table = []
        for j in range(trc.model.K):
            bounds = smtirf.where(trc.SP == j)
            lengths = np.diff(bounds, axis=1)
            state = np.ones((bounds.shape[0], 1))*j
            mu = np.ones((bounds.shape[0],1))*trc.model.mu[j]
            try:
                xbar = np.hstack([np.median(trc.X[slice(*bound)]) for bound in bounds])
                xbar = xbar[:,np.newaxis]
            except ValueError:
                xbar = np.zeros(lengths.shape) # empty
            table.append(np.hstack((bounds, state, lengths, mu, xbar)))
        table = np.vstack(table)
        self.table = table[np.argsort(table[:,0]),:]

    def get_transitions(self, dataType="fit"):
        if dataType.lower() == "fit":
            col = 4
        elif dataType.lower() == "data":
            col = 5
        elif dataType.lower() == "state":
            col = 3
        else:
            raise ValueError("dataType not recognized")
        return np.vstack((self.table[:-1,col], self.table[1:,col])).T

    def get_dwelltimes(self, start, stop):
        ixStart = (self.table[1:-1,2] == start)
        ixStop = (self.table[2:,2] == stop)
        ix = np.logical_and(ixStart, ixStop)
        try:
            return self.table[1:-1,3].squeeze()[ix]
        except IndexError:
            return []


# ==============================================================================
# module functions
# ==============================================================================
def get_split_histogram(e, minimum=-0.2, maximum=1.2, nBins=75):
    # TODO ==> density normalization !!

    # extract full dataset
    X = np.hstack([trc.X for trc in e if trc.isSelected])
    S = np.hstack([trc.SP for trc in e if trc.isSelected])
    # replace NaN's and Inf's
    X[np.argwhere(np.logical_not(np.isfinite(X)))] = np.nan

    bins, width = np.linspace(minimum, maximum, nBins, retstep=True)
    total, _ = np.histogram(X, bins=bins)

    populations = []    # state populations
    states = []         # state histograms
    for k in range(S.max()+1):
        xx = X[S==k]
        populations.append(xx.size/X.size)
        n, edges = np.histogram(xx, bins=bins)
        states.append(n)
    centers = edges[:-1] + width/2
    # centers, total, states, binWidth
    return centers, total, np.vstack(states), width


def get_tdp(e, minimum=-0.2, maximum=1.2, nBins=150, bandwidth=0.04, dataType="fit"):
    X = np.vstack([trc.dwells.get_transitions(dataType=dataType) for trc in e if trc.isSelected])
    # replace NaN's and Inf's
    X[np.where(np.logical_not(np.isfinite(X)))] = np.nan

    mesh = np.linspace(minimum, maximum, nBins)
    XX,YY = np.meshgrid(mesh,mesh)
    coords = np.vstack((XX.ravel(), YY.ravel())).T

    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(X)
    ZZ = np.exp(kde.score_samples(coords)).reshape(XX.shape)
    return XX, YY, ZZ
