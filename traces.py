# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> traces
"""
import numpy as np
import scipy.stats
import json, warnings
from abc import ABC, abstractmethod
import smtirf
from . import SMSpotCoordinate, SMJsonEncoder
from . import HiddenMarkovModel

# ==============================================================================
# BASE TRACE CLASSES
# ==============================================================================
class BaseTrace(ABC):

    def __init__(self, trcID, data, frameLength, pk, bleed, gamma, clusterIndex=-1,
                 isSelected=False, limits=None, offsets=None, model=None, deBlur=False, deSpike=False):
        self._id = trcID
        self._set_data(data)
        self.set_frame_length(frameLength) # => set self.t
        self._bleed = bleed
        self._gamma = gamma
        self.set_offsets(offsets) # => triggers _correct_signals()
        self.set_limits(limits, refreshStatePath=False)

        self.pk = SMSpotCoordinate(pk)
        self.isSelected = isSelected
        self.set_cluster_index(clusterIndex)
        self.model = HiddenMarkovModel.from_json(model)
        self.deBlur = deBlur
        self.deSpike = deSpike
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

    @property
    def _attr_dict(self):
        return {"pk" : self.pk,
                "clusterIndex" : self.clusterIndex,
                "frameLength" : self.frameLength,
                "bleed" : self.bleed,
                "gamma" : self.gamma,
                "limits" : self.limits,
                "offsets" : self.offsets,
                "isSelected" : self.isSelected,
                "deBlur" : self.deBlur,
                "deSpike" : self.deSpike}

    def _as_json(self):
        return json.dumps(self._attr_dict, cls=SMJsonEncoder)


    @property
    def SP(self): # state path
        return self._SP[self.limits].astype(np.int)

    def set_statepath(self, sp):
        SP = np.full(self._SP.shape, -1)
        SP[self.limits] = sp
        self._SP = SP

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
    def clusterIndex(self):
        return self._clusterIndex

    def set_cluster_index(self, val):
        #TODO => catch ValueError for non-int val
        self._clusterIndex = int(val)

    @property
    def movID(self):
        return self._id.movID

    @property
    def I0(self):
        return self.D0 + self.A0

    @property
    def corrcoef(self):
        return scipy.stats.pearsonr(self.D[self.limits], self.A[self.limits])[0]

    def _time2frame(self, t): # copy from old
        # find frame index closest to time t
        return np.argmin(np.abs(self.t-t))

    def set_offset_time_window(self, start, stop):
        rng = slice(self._time2frame(start), self._time2frame(stop))
        self.set_offsets([np.median(self.D0[rng]), np.median(self.A0[rng])])

    def set_start_time(self, time, refreshStatePath=True):
        fr = self._time2frame(time)
        self.set_limits([fr, self.limits.stop], refreshStatePath=refreshStatePath)

    def set_stop_time(self, time, refreshStatePath=True):
        fr = self._time2frame(time)
        self.set_limits([self.limits.start, fr], refreshStatePath=refreshStatePath)

    def toggle(self):
        self.isSelected = not self.isSelected

    def set_signal_labels(self, sp, where="first", correctOffsets=True):
        self.S0 = sp
        if correctOffsets:
            if np.any(sp == 2):
                rng, = np.where(sp == 2)
            elif np.any(sp == 1):
                rng, = np.where(sp == 1)
            try:
                self.set_offsets([np.median(self.D0[rng]), np.median(self.A0[rng])])
            except UnboundLocalError:
                pass
        # find indices of signal dwells
        if where.lower() in ("first", "longest"):
            ix = smtirf.where(sp == 0)
        # set limits
        if where.lower() == "first":
            self.set_limits(ix[0])
        elif where.lower() == "longest":
            dt = np.diff(ix, axis=1).squeeze()
            self.set_limits(ix[np.argmax(dt)])
        elif where.lower() == "all":
            pass
        else:
            raise ValueError("where keyword unrecognized")

    # def reset_signal_labels(self):
    #     self.S0 = np.zeros(self.S0.shape)
    #     self._correct_signals() # this really should be implemented as a setter for all S0 changes
    #
    def reset_offsets(self):
        self.set_offsets((0, 0))

    def reset_limits(self):
        self.set_limits((0, len(self)))

    @property
    @abstractmethod
    def X(self):
        ...

    def train(self, modelType, K, sharedVariance=True, **kwargs):
        theta = smtirf.HiddenMarkovModel.train_new(modelType, self.X, K, sharedVariance, **kwargs)
        self.model = theta
        self.label_statepath()

    def label_statepath(self):
        if self.model is not None:
            self.set_statepath(self.model.label(self.X, deBlur=self.deBlur, deSpike=self.deSpike))
            # self.dwells = DwellTable(self)

    @property
    def EP(self):
        return self.model.get_emission_path(self.SP)

# ==============================================================================
# Experiment Trace Subclasses
# ==============================================================================
class SingleColorTrace(BaseTrace):

    def __init__(self, trcID, data, frameLength, pk, bleed, gamma, channel=1, **kwargs):
        super().__init__(trcID, data, frameLength, pk, bleed, gamma, **kwargs)
        self.channel = channel

    @property
    def _attr_dict(self):
        d = super()._attr_dict
        d["channel"] = self.channel
        return d

    def __str__(self):
        s = super().__str__()
        s += f" [Channel {self.channel}]"
        return s

    @property
    def X(self):
        return self.D[self.limits] if self.channel == 1 else self.A[self.limits]

class PifeTrace(SingleColorTrace):

    pass

    # @property
    # def X(self):
    #     return 2


# class PifeCh2Trace(BaseTrace):
#
#     @property
#     def X(self):
#         return 3


class MultimerTrace(SingleColorTrace):

    def train(self, K, sharedVariance=True, **kwargs):
        theta = smtirf.HiddenMarkovModel.train_new("multimer", self.X, K, sharedVariance, **kwargs)
        self.model = theta
        self.label_statepath()

    # def train(self, K, modelType="multimer", guess_with_kmeans=False, sharedVariance=True, printWarnings=False):
    #     theta = smtirf.HiddenMarkovModel.new(K, self.X, modelType=modelType,
    #                                          guess_with_kmeans=guess_with_kmeans,
    #                                          sharedVariance=sharedVariance,
    #                                          trainNow=True, printWarnings=printWarnings)
    #     self.model = theta
    #     self.label_statepath()


class FretTrace(BaseTrace):

    @property
    def X(self):
        return self.E[self.limits]

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
