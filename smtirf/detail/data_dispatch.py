from .definitions import Coordinates
from .metadata import TraceMetadata


class TraceDataDispatcher:
    def __init__(self, file_handle, uid):
        self.file_handle = file_handle
        print(uid)
        self.movie_uid, index = uid.split("_")
        self.index = int(index)

        self.movie_path = f"movies/movie_{self.movie_uid}"

    def get_metadata(self):
        record = self.file_handle[self.movie_path]["traces/metadata"][self.index]
        record = dict(zip(record.dtype.names, record))
        record["n_frames"] = self.file_handle[self.movie_path].attrs["n_frames"]
        record["movie_uid"] = self.movie_uid
        record["index"] = self.index
        return TraceMetadata.from_record_dict(record)
