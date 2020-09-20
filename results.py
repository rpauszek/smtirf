# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> results
"""
from datetime import datetime
import json
import numpy as np
from sklearn.neighbors import KernelDensity

from . import SMJsonEncoder
import smtirf

class Results():

    def __init__(self, expt, hist=None, tdp=None):
        self._expt = expt
        self.hist = Histogram(expt) if hist is None else Histogram(expt, **hist)
        self.tdp = Tdp(expt) if tdp is None else Tdp(expt, **tdp)


# ==============================================================================
# AGGREGATE RESULT CLASSES
# ==============================================================================
class Histogram():

    def __init__(self, expt, data=None, populations=None, minimum=-0.2, maximum=1.2, nBins=75):
        self._expt = expt
        self._set_data(data)
        self.populations = populations
        self.minimum = minimum
        self.maximum = maximum
        self.nBins = nBins

    def _set_data(self, data):
        if data is None:
            self.total = None
            self.states = None
        else:
            self.total = data[0]
            self.states = data[1:]

    @property
    def _raw_data(self):
        return np.vstack((self.total, self.states))

    @property
    def _attr_dict(self):
        return {"populations" : self.populations,
                "minimum" : self.minimum,
                "maximum" : self.maximum,
                "nBins" : self.nBins}

    def _as_json(self):
        return json.dumps(self._attr_dict, cls=SMJsonEncoder)

    @property
    def edges(self):
        return np.linspace(self.minimum, self.maximum, self.nBins+1, retstep=False)

    @property
    def width(self):
        return self.edges[0]-self.edges[1]

    @property
    def centers(self):
        return self.edges[:-1] + self.width/2


    def calculate(self):#, minimum=-0.2, maximum=1.2, nBins=75):
        # TODO ==> density normalization !!

        # extract full dataset
        X = np.hstack([trc.X for trc in self._expt if trc.isSelected and trc.model is not None])
        S = np.hstack([trc.SP for trc in self._expt if trc.isSelected and trc.model is not None])
        # remove NaN's and Inf's
        X = X[np.argwhere(np.isfinite(X))]

        self.total, _ = np.histogram(X, bins=self.edges)
        populations = []    # state populations
        states = []         # state histograms
        for k in range(S.max()+1):
            xx = X[S==k]
            populations.append(xx.size/X.size)
            n, _ = np.histogram(xx, bins=self.edges)
            states.append(n)
        self.populations = np.hstack(populations)
        self.states = np.vstack(states)


class Tdp():

    def __init__(self, expt, data=None, minimum=-0.2, maximum=1.2, nBins=150, bandwidth=0.04, dataType="data"):
        self._expt = expt
        self._set_data(data)
        self.minimum = minimum
        self.maximum = maximum
        self.nBins = nBins
        self.bandwidth = bandwidth
        self.dataType = dataType

    def _set_data(self, data):
        if data is None:
            self.X = None
            self.Y = None
            self.Z = None
        else:
            self.X = data[:,:,0]
            self.Y = data[:,:,1]
            self.Z = data[:,:,2]

    @property
    def _raw_data(self):
        return np.stack((self.X, self.Y, self.Z), axis=2)

    @property
    def _attr_dict(self):
        return {"minimum" : self.minimum,
                "maximum" : self.maximum,
                "nBins" : self.nBins,
                "bandwidth" : self.bandwidth,
                "dataType" : self.dataType}

    def _as_json(self):
        return json.dumps(self._attr_dict, cls=SMJsonEncoder)

    @property
    def mesh(self):
        return np.linspace(self.minimum, self.maximum, self.nBins)

    def calculate(self):
        X = np.vstack([trc.dwells.get_transitions(dataType=self.dataType)
                       for trc in self._expt if trc.isSelected and trc.model is not None])
        # # replace NaN's and Inf's
        # X[np.where(np.logical_not(np.isfinite(X)))] = np.nan

        self.X, self.Y = np.meshgrid(self.mesh,self.mesh)
        coords = np.vstack((self.X.ravel(), self.Y.ravel())).T

        kde = KernelDensity(kernel='gaussian', bandwidth=self.bandwidth).fit(X)
        self.Z = np.exp(kde.score_samples(coords)).reshape(self.X.shape)



# ==============================================================================
# DWELLTIMES
# ==============================================================================
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
            col = 2
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
