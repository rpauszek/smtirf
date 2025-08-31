from functools import wraps

import numpy as np
import scipy.stats

import smtirf

from .detail.data_dispatch import FretDispatcher, TraceLoader, TwoColorDispatcher
from .hmm.models import HiddenMarkovModel


def with_statepath_update(func):
    """
    Decorator to ensure that the model statepath is updated when the signal is changed
    (eg, channel offsets or range limits changed).
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)  # run original method
        self._update_statepath()
        return result

    return wrapper


class Trace:
    def __init__(self, file_handle, uid):
        self._loader = TraceLoader(file_handle, uid)
        self._metadata = self._loader.get_metadata()

        # todo: should this be mutable?
        self._gamma = self._loader.gamma
        self._bleed = self._loader.bleedthrough

        match (t := self._loader.experiment_type):
            case "fret":
                dispatcher_cls = FretDispatcher
            case "twocolor":
                dispatcher_cls = TwoColorDispatcher
            case _:
                raise NotImplementedError(
                    f"dispatcher is not implemented for experiment type {t}"
                )

        self._raw_dispatcher = dispatcher_cls(
            lambda: np.arange(self._metadata.n_frames) * self.frame_length,
            lambda: self._loader.get_data("channel_1"),
            lambda: self._loader.get_data("channel_2"),
        )

        self._baselined_dispatcher = dispatcher_cls(
            lambda: self.raw.time,
            lambda: self.raw._channel_1() - self._metadata.ch1_offset,
            lambda: self.raw._channel_2() - self._metadata.ch2_offset,
        )

        self._corrected_dispatcher = dispatcher_cls(
            lambda: self.raw.time,
            lambda: self._baselined_dispatcher._channel_1() * self._gamma,
            lambda: self._baselined_dispatcher._channel_2()
            - (self._baselined_dispatcher._channel_1() * self._bleed),
        )

        self._final_dispatcher = dispatcher_cls(
            lambda: self.raw.time[self._metadata.selected_slice],
            lambda: self.corrected._channel_1()[self._metadata.selected_slice],
            lambda: self.corrected._channel_2()[self._metadata.selected_slice],
        )

        self._photophysics_statepath = self._loader.get_statepath("photophysics")
        self._statepath = self._loader.get_statepath("conformation")
        self._model = None  # todo: placeholder until HMM refactor

    def __str__(self):
        return (
            f"{self.__class__.__name__}\tID={self._metadata.trace_uid}"
            f"\tselected={self._metadata.is_selected}"
        )

    def __len__(self):
        return self._loader.n_frames

    @property
    def frame_length(self):
        return self._loader.frame_length

    @property
    def bleed(self):
        return self._bleed

    @property
    def gamma(self):
        return self._gamma

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
    def total(self):
        return self._final_dispatcher.total

    @property
    def corrcoef(self):
        return scipy.stats.pearsonr(self.donor, self.acceptor)[0]

    @property
    def state_path(self):
        if self._model is None:
            raise ValueError("No model exists for this trace.")
        # todo: test, ensure int
        return self._statepath[self._metadata.selected_slice]

    def _update_statepath(self):
        # todo: check old implementation, label_statepath(), recalculate dwell table ?
        # todo: potentially include clearing statepath if model is removed
        if self.is_selected and self._model is not None:
            print("updating statepath...")

    @property
    def emission_path(self):
        return self.model.get_emission_path(self.state_path)

    @property
    def is_selected(self):
        return self._metadata.is_selected

    @with_statepath_update
    def set_selected(self, value):
        if not isinstance(value, bool):
            raise ValueError("value must be of type bool.")
        self._metadata.is_selected = value

    @with_statepath_update
    def toggle_selected(self):
        self._metadata.is_selected = not self.is_selected

    @property
    def offsets(self):
        return [self._metadata.donor_offset, self._metadata.acceptor_offset]

    @with_statepath_update
    def set_offsets(self, values):
        if len(values) != 2:
            raise ValueError("must provide offsets for both (2) channels")
        self._metadata.ch1_offset = values[0]
        self._metadata.ch2_offset = values[1]

    def reset_offsets(self):
        self.set_offsets((0, 0))

    # todo: set_offsets_from_time_range()

    @property
    def limits(self):
        return [self._metadata.start, self._metadata.stop]

    # todo: set_start_time()
    # todo: set_stop_time()

    @with_statepath_update
    def set_limits(self, start=None, stop=None):
        """Set start/stop limits of analysis range by frame index."""
        # todo: original function had bool refreshStatePath
        # todo: check that unneccessary viterbi doesn't happen on construction

        match (start, stop):
            case (None, None):
                raise ValueError(
                    "At least one of start/stop must be provided. If you wish to reset "
                    "the limits to the full trace call the reset_limits() method."
                )
            case (s, _) if s is not None and s < 0:
                raise ValueError("Start must be non-negative.")
            case (_, e) if e is not None and e < 0:
                raise ValueError("Stop must be non-negative.")
            case (s, e) if s is not None and e is not None and s >= e:
                raise ValueError("Start must be less than stop.")
            case (_, e) if e is not None and e >= len(self):
                raise ValueError("Stop must be less than trace length.")
            case _:
                self._metadata.start = start
                self._metadata.stop = stop

    def reset_limits(self):
        self.set_limits((0, len(self)))

    # todo: fixup with autobaseline refactor
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

    def get_export_data(self):
        raise NotImplementedError("Base class does not implement this method.")

    def export(self, savename):
        data, fmt, header = self.get_export_data()
        np.savetxt(savename, data, fmt=fmt, delimiter="\t", header=header)


class FretTrace(Trace):
    @property
    def donor(self):
        return self._final_dispatcher.donor

    @property
    def acceptor(self):
        return self._final_dispatcher.acceptor

    @property
    def fret(self):
        return self._final_dispatcher.fret


class TwoColorTrace(Trace):
    @property
    def channel_1(self):
        return self._final_dispatcher.channel_1

    @property
    def channel_2(self):
        return self._final_dispatcher.channel_2
