# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> results
"""
import numpy as np
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
