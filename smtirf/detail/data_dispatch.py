from dataclasses import dataclass
from typing import Callable

from .metadata import TraceMetadata


@dataclass(repr=False)
class DataDispatcher:
    _time: Callable
    _donor: Callable
    _acceptor: Callable

    @property
    def time(self):
        return self._time()

    @property
    def donor(self):
        return self._donor()

    @property
    def acceptor(self):
        return self._acceptor()

    @property
    def total(self):
        return self.donor + self.acceptor

    @property
    def fret(self):
        return self.acceptor / self.total


class TraceDataDispatcher:
    def __init__(self, file_handle, uid):
        self.file_handle = file_handle
        self.movie_uid, index = uid.split("_")
        self.index = int(index)
        self.movie_path = f"movies/movie_{self.movie_uid}"

    def get_metadata(self):
        # todo: validate trace uid matches expected
        record = self.file_handle[self.movie_path]["traces/metadata"][self.index]
        record = dict(zip(record.dtype.names, record))
        record["n_frames"] = self.n_frames
        record["movie_uid"] = self.movie_uid
        record["index"] = self.index
        return TraceMetadata.from_record_dict(record)

    def get_data(self, kind):
        if kind not in ("donor, acceptor"):
            raise ValueError(f"kind must be 'donor' or 'acceptor; got '{kind}'")
        return self.file_handle[self.movie_path][f"traces/{kind}_traces"][self.index]

    def get_statepath(self, kind):
        if kind not in ("conformation, photophysics"):
            raise ValueError(
                f"kind must be 'conformation' or 'photophysics; got '{kind}'"
            )
        return self.file_handle[self.movie_path][f"statepaths/conformation"][self.index]

    @property
    def frame_length(self):
        return self.file_handle[self.movie_path].attrs["frame_length"]

    @property
    def n_frames(self):
        return self.file_handle[self.movie_path].attrs["n_frames"]
