import json
import warnings
from abc import ABC, abstractmethod

import numpy as np
import scipy.stats

import smtirf

from . import SMJsonEncoder, SMSpotCoordinate
from .detail.data_dispatch import DataDispatcher, TraceDataDispatcher
from .hmm.models import HiddenMarkovModel


class Trace:
    def __init__(self, file_handle, uid):
        self._dispatcher = TraceDataDispatcher(file_handle, uid)
        self._metadata = self._dispatcher.get_metadata()

        # todo: handle this properly
        self._gamma = 1
        self._bleed = 0.05

        self._raw_dispatcher = DataDispatcher(
            lambda: np.arange(self._metadata.n_frames) * self.frame_length,
            lambda: self._dispatcher.get_data("donor"),
            lambda: self._dispatcher.get_data("acceptor"),
        )

        self._baselined_dispatcher = DataDispatcher(
            lambda: self.raw.time,
            lambda: self.raw.donor - self._metadata.donor_offset,
            lambda: self.raw.acceptor - self._metadata.acceptor_offset,
        )

        self._corrected_dispatcher = DataDispatcher(
            lambda: self.raw.time,
            lambda: self._baselined_dispatcher.donor * self._gamma,
            lambda: self._baselined_dispatcher.acceptor
            - (self._baselined_dispatcher.donor * self._bleed),
        )

        self._final_dispatcher = DataDispatcher(
            lambda: self.raw.time[self._metadata.selected_slice],
            lambda: self.corrected.donor[self._metadata.selected_slice],
            lambda: self.corrected.acceptor[self._metadata.selected_slice],
        )

        self._photophysics_statepath = self._dispatcher.get_statepath("photophysics")
        self._statepath = self._dispatcher.get_statepath("conformation")
        self._model = None  # todo: placeholder until HMM refactor

        # self.set_cluster_index(clusterIndex)
        # self.model = HiddenMarkovModel.from_json(model)
        # self.deBlur = deBlur
        # self.deSpike = deSpike
        # self.dwells = (
        #     smtirf.results.DwellTable(self) if self.model is not None else None
        # )

    def __str__(self):
        return (
            f"{self.__class__.__name__}\tID={self._metadata.trace_uid}"
            f"\tselected={self._metadata.is_selected}"
        )

    def __len__(self):
        return self._dispatcher.n_frames

    @property
    def raw(self):
        return self._raw_dispatcher

    @property
    def corrected(self):
        return self._corrected_dispatcher

    @property
    def time(self):
        return self._final_dispatcher.time

    @property
    def donor(self):
        return self._final_dispatcher.donor

    @property
    def acceptor(self):
        return self._final_dispatcher.acceptor

    @property
    def total(self):
        return self._final_dispatcher.total

    @property
    def fret(self):
        return self._final_dispatcher.fret

    @property
    def state_path(self):
        if self._model is None:
            raise ValueError("No model exists for this trace.")
        # todo: test, ensure int
        return self._statepath[self._metadata.selected_slice]

    @property
    def emission_path(self):
        return self.model.get_emission_path(self.state_path)

    @property
    def is_selected(self):
        return self._metadata.is_selected

    def toggle_selected(self):
        self._metadata.is_selected = not self.is_selected

    @property
    def _attr_dict(self):
        return {
            "pk": self.pk,
            "clusterIndex": self.clusterIndex,
            "frameLength": self.frameLength,
            "bleed": self.bleed,
            "gamma": self.gamma,
            "limits": self.limits,
            "offsets": self.offsets,
            "isSelected": self.isSelected,
            "deBlur": self.deBlur,
            "deSpike": self.deSpike,
        }

    def _as_json(self):
        return json.dumps(self._attr_dict, cls=SMJsonEncoder)

    @property
    def frame_length(self):
        return self._dispatcher.frame_length

    @property
    def bleed(self):
        return self._bleed

    @property
    def gamma(self):
        return self._gamma

    @property
    def offsets(self):
        return [self._metadata.donor_offset, self._metadata.acceptor_offset]

    def set_offsets(self, values):
        if len(values) != 2:
            raise ValueError("must provide offsets for both (2) channels")
        self._metadata.donor_offset = values[0]
        self._metadata.acceptor_offset = values[1]

    def reset_offsets(self):
        self.set_offsets((0, 0))

    @property
    def limits(self):
        return [self._metadata.start, self._metadata.stop]

    def set_limits(self, values, refreshStatePath=True):
        if values is None:
            self._limits = slice(*np.array([0, len(self)]))
        elif not isinstance(values, slice):
            values = np.array(values)
            if values.size != 2:
                raise ValueError("must provide offsets for both (2) channels")
            values = np.sort(values)
            if values[0] < 0:
                values[0] = 0  # TODO: add warning?
            if values[1] > len(self):
                values[1] = len(self)  # TODO: add warning?
            if np.diff(values) <= 2:
                warnings.warn("range must be >2 frames. resetting to full trace")
                values = np.array([0, len(self)])  # TODO: maybe just don't update?
            self._limits = slice(*values)
        else:
            self._limits = values
        if refreshStatePath:
            self.label_statepath()

    @property
    def clusterIndex(self):
        return self._clusterIndex

    def set_cluster_index(self, val):
        # TODO => catch ValueError for non-int val
        self._clusterIndex = int(val)

    @property
    def movID(self):
        return self._id.movID

    @property
    def corrcoef(self):
        return scipy.stats.pearsonr(self.donor, self.acceptor)[0]

    def _time2frame(self, t):  # copy from old
        # find frame index closest to time t
        return np.argmin(np.abs(self.t - t))

    def set_offset_time_window(self, start, stop):
        rng = slice(self._time2frame(start), self._time2frame(stop))
        self.set_offsets([np.median(self.D0[rng]), np.median(self.A0[rng])])

    def set_start_time(self, time, refreshStatePath=True):
        fr = self._time2frame(time)
        self.set_limits([fr, self.limits.stop], refreshStatePath=refreshStatePath)

    def set_stop_time(self, time, refreshStatePath=True):
        fr = self._time2frame(time)
        self.set_limits([self.limits.start, fr], refreshStatePath=refreshStatePath)

    def set_signal_labels(self, sp, where="first", correctOffsets=True):
        self.S0 = sp
        if correctOffsets:
            if np.any(sp == 2):
                (rng,) = np.where(sp == 2)
            elif np.any(sp == 1):
                (rng,) = np.where(sp == 1)
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

    def reset_limits(self):
        self.set_limits((0, len(self)))

    def train(self, modelType, K, sharedVariance=True, **kwargs):
        theta = smtirf.HiddenMarkovModel.train_new(
            modelType, self.X, K, sharedVariance, **kwargs
        )
        self.model = theta
        self.label_statepath()

    def label_statepath(self):
        if self.model is not None:
            self.set_statepath(
                self.model.label(self.X, deBlur=self.deBlur, deSpike=self.deSpike)
            )
            self.dwells = smtirf.results.DwellTable(self)

    @abstractmethod
    def get_export_data(self):
        ...

    def export(self, savename):
        data, fmt, header = self.get_export_data()
        np.savetxt(savename, data, fmt=fmt, delimiter="\t", header=header)


class SingleColorTrace:
    def __init__(self, trcID, data, frameLength, pk, bleed, gamma, channel=1, **kwargs):
        self.channel = channel
        super().__init__(trcID, data, frameLength, pk, bleed, gamma, **kwargs)

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


class PifeTrace:
    classLabel = "pife"

    def get_export_data(self):
        pass


class MultimerTrace:
    classLabel = "multimer"

    def train(self, K, sharedVariance=True, **kwargs):
        theta = smtirf.HiddenMarkovModel.train_new(
            "multimer", self.X, K, sharedVariance, **kwargs
        )
        self.model = theta
        self.label_statepath()

    def get_export_data(self):
        pass


class FretTrace:
    classLabel = "fret"

    @property
    def X(self):
        return self.E[self.limits]

    def _correct_signals(self):
        super()._correct_signals()
        with np.errstate(divide="ignore", invalid="ignore"):
            self.E = self.A / self.I

    def get_export_data(self):
        E = np.full(self.E.shape, np.nan)
        S = np.full(self.E.shape, -1)
        F = E.copy()
        E[self.limits] = self.X
        try:
            S[self.limits] = self.SP
            F[self.limits] = self.EP
        except AttributeError:
            pass
        data = np.vstack((self.t, self.D, self.A, E, S, F)).T
        fmt = ("%.3f", "%.3f", "%.3f", "%.5f", "%3d", "%.5f")
        header = "Time (sec)\tDonor\tAcceptor\tFRET\tState\tFit"
        return data, fmt, header


class PiecewiseTrace(FretTrace):
    classLabel = "piecewise"

    @property
    def X(self):
        return 1

    def _correct_signals(self):
        super()._correct_signals()
        self._E = (
            self.E.copy()
        )  # store a normal version of FRET efficiency, without masking
        self.E[self.S0 != 0] = np.nan
