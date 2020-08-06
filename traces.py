# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> traces
"""
import numpy as np
from abc import ABC, abstractmethod
from . import SMSpotCoordinate

# ==============================================================================
# BASE TRACE CLASSES
# ==============================================================================
class BaseTrace(ABC):

    def __init__(self, trcID, data, frameLength, pk, bleed, gamma, clusterIndex=-1,
                 isSelected=False, limits=None, offsets=None, model=None):
        self._id = trcID
        self._set_data(data)
        self.set_frame_length(frameLength) # => set self.t
        self._bleed = bleed
        self._gamma = gamma
        self.set_offsets(offsets) # => triggers _correct_signals()
        self.set_limits(limits, refreshStatePath=False)

        self.pk = SMSpotCoordinate(pk)
        self.isSelected = isSelected
        self.clusterIndex = clusterIndex
        self.model = model
        self.dwells = None #DwellTable(self) if self.model is not None else None

    def __str__(self):
        return f"{self.__class__.__name__}\tID={self._id}  selected={self.isSelected}"

    def __len__(self):
        return self.D0.size

    def _set_data(self, data):
        self.D0, self.A0, self.S0, self._SP = data

    @property
    def _raw_data(self):
        return np.vstack((self.D0, self.A0, self.S0, self._SP))

    def _as_json(self):
        return {"pk" : self.pk,
                "clusterIndex" : self.clusterIndex,
                "frameLength" : self.frameLength,
                "bleed" : self.bleed,
                "gamma" : self.gamma,
                "limits" : self.limits,
                "offsets" : self.offsets,
                "isSelected" : self.isSelected}

    @property
    def SP(self): # state path
        return self._SP#[self.limits].astype(np.int)

    @property
    def frameLength(self):
        return self._frameLength

    @property
    def bleed(self):
        return self._bleed

    @property
    def gamma(self):
        return self._gamma

    def set_frame_length(self, val):
        self._frameLength = val
        self.t = np.arange(len(self))*self._frameLength

    def set_bleed(self, val):
        if val >= 0 and val <=1:
            self._bleed = val
            self._correct_signals()
        else:
            raise ValueError("donor bleedthrough must be between 0 and 1")

    def set_gamma(self, val):
        if val > 0 and val <=2:
            self._gamma = val
            self._correct_signals()
        else:
            raise ValueError("gamma must be between 0 and 2")

    @property
    def offsets(self):
        return self._offsets

    def set_offsets(self, values):
        if values is None:
            values = np.zeros(2)
        elif len(values) !=2:
                raise ValueError("must provide offsets for both (2) channels")
        self._offsets = np.array(values)
        self._correct_signals()

    def _correct_signals(self):
        D = self.D0 - self._offsets[0]
        A = self.A0 - self._offsets[1]
        self.D = D * self._gamma
        self.A = A - (D*self._bleed)
        self.I = self.D + self.A

    @property
    def limits(self):
        return self._limits # Slice instance

    def set_limits(self, values, refreshStatePath=True):
        if values is None:
            self._limits = slice(*np.array([0, len(self)]))
        elif not isinstance(values, slice):
            values = np.array(values)
            if values.size !=2:
                raise ValueError("must provide offsets for both (2) channels")
            values = np.sort(values)
            if values[0] < 0: values[0] = 0                 # TODO: add warning?
            if values[1] > len(self): values[1] = len(self) # TODO: add warning?
            if np.diff(values) <= 2:
                warnings.warn("range must be >2 frames. resetting to full trace")
                values = np.array([0, len(self)]) # TODO: maybe just don't update?
            self._limits = slice(*values)
        else:
            self._limits = values
        if refreshStatePath:
            self.label_statepath()

    @property
    @abstractmethod
    def X(self):
        ...


# ==============================================================================
# Experiment Trace Subclasses
# ==============================================================================
class PifeTrace(BaseTrace):

    @property
    def X(self):
        return 2


class PifeCh2Trace(BaseTrace):

    @property
    def X(self):
        return 3


class MultimerTrace(BaseTrace):

    @property
    def X(self):
        return 4


class FretTrace(BaseTrace):

    @property
    def X(self):
        return 0

    def _correct_signals(self):
        super()._correct_signals()
        with np.errstate(divide='ignore', invalid='ignore'):
            self.E = self.A / self.I


class PiecewiseTrace(FretTrace):

    @property
    def X(self):
        return 1

    def _correct_signals(self):
        super()._correct_signals()
        self._E = self.E.copy() # store a normal version of FRET efficiency, without masking
        self.E[self.S0 != 0] = np.nan
