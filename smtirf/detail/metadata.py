import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import dacite
import h5py
import numpy as np

from .definitions import Coordinates

# todo: look into log timestamp is still string -> json decoder?
config = dacite.Config(
    type_hooks={
        int: lambda v: int(v) if isinstance(v, np.integer) else v,
        datetime: lambda t: datetime.fromisoformat(t),
        dict: lambda d: json.loads(d),
    }
)


@dataclass(frozen=True)
class MovieMetadata:
    n_traces: int
    n_frames: int
    src_filename: str
    timestamp: datetime
    frame_length: float
    ccd_gain: int
    data_scaler: Optional[int] = None
    log: Optional[dict] = field(default_factory=dict, repr=False)

    @classmethod
    def _from_group(cls, group):
        return dacite.from_dict(cls, dict(group.attrs), config=config)

    @property
    def uid(self):
        return self.timestamp.strftime("%Y%m%dT%H%M%S")


TRACE_DTYPE = np.dtype(
    [
        ("trace_id", h5py.string_dtype("utf-8", length=32)),
        ("donor_x", np.float32),
        ("donor_y", np.float32),
        ("acceptor_x", np.float32),
        ("acceptor_y", np.float32),
        ("start", np.uint32),
        ("stop", np.uint32),
        ("donor_offset", np.float32),
        ("acceptor_offset", np.float32),
        ("is_selected", bool),
    ]
)


@dataclass(frozen=True)
class TraceMetadata:
    movie_uid: str
    n_frames: int
    index: Optional[int] = None
    peak: Optional[Coordinates] = None
    start: Optional[int] = 0
    stop: Optional[int] = None
    donor_offset: Optional[int] = 0
    acceptor_offset: Optional[int] = 0
    is_selected: Optional[bool] = False

    @classmethod
    def from_movie_metadata(cls, movie_metadata):
        """Make a factory based on movie UID and length."""
        return cls(movie_metadata.uid, movie_metadata.n_frames)

    @property
    def trace_uid(self):
        if self.index is None:
            raise ValueError("trace index is not set.")

        return f"{self.movie_uid}_{self.index:04d}"

    def make_trace_uid(self, index):
        """Return a Trace UID for a given index using the current Movie UID"""
        return f"{self.movie_uid}_{index:04d}"

    def make_record(self, *, index=None, peak=None):
        # todo: throw if kwargs but already set in instance

        trace_uid = [
            self.trace_uid if self.index is not None else self.make_trace_uid(index)
        ]
        peak = self.peak if self.peak is not None else peak
        stop = self.stop if self.stop is not None else self.n_frames

        return tuple(
            trace_uid
            + peak.as_list()
            + [
                self.start,
                stop,
                self.donor_offset,
                self.acceptor_offset,
                self.is_selected,
            ]
        )
