from dataclasses import dataclass
from typing import Callable

from .metadata import TraceMetadata


@dataclass(repr=False)
class SignalDispatcher:
    _time: Callable
    _channel_1: Callable
    _channel_2: Callable

    @property
    def time(self):
        return self._time()

    @property
    def total(self):
        return self._channel_1() + self._channel_2()


@dataclass(repr=False)
class FretDispatcher(SignalDispatcher):
    @property
    def donor(self):
        return self._channel_1()

    @property
    def acceptor(self):
        return self._channel_2()

    @property
    def fret(self):
        return self.acceptor / self.total


@dataclass(repr=False)
class TwoColorDispatcher(SignalDispatcher):
    @property
    def channel_1(self):
        return self._channel_1()

    @property
    def channel_2(self):
        return self._channel_2()


class TraceLoader:
    def __init__(self, file_handle, uid):
        self.file_handle = file_handle
        self.movie_uid, index = uid.split("_")
        self.index = int(index)
        self.movie_path = f"movies/movie_{self.movie_uid}"

    def get_metadata(self):
        # todo: validate trace uid matches expected
        record = self.file_handle[self.movie_path]["traces/metadata"][self.index]
        record = dict(zip(record.dtype.names, record, strict=False))
        record["n_frames"] = self.n_frames
        record["movie_uid"] = self.movie_uid
        record["index"] = self.index
        return TraceMetadata.from_record_dict(record)

    def get_data(self, kind):
        if kind not in ("channel_1, channel_2"):
            raise ValueError(f"kind must be 'channel_1' or 'channel_2; got '{kind}'")
        return self.file_handle[self.movie_path][f"traces/{kind}"][self.index]

    def get_statepath(self, kind):
        if kind not in ("conformation, photophysics"):
            raise ValueError(
                f"kind must be 'conformation' or 'photophysics; got '{kind}'"
            )
        return self.file_handle[self.movie_path]["statepaths/conformation"][self.index]

    @property
    def experiment_type(self):
        return self.file_handle.attrs["experiment_type"]

    @property
    def frame_length(self):
        return self.file_handle[self.movie_path].attrs["frame_length"]

    @property
    def n_frames(self):
        return self.file_handle[self.movie_path].attrs["n_frames"]

    @property
    def bleedthrough(self):
        return self.file_handle.attrs["bleedthrough"]

    @property
    def gamma(self):
        return self.file_handle.attrs["gamma"]
