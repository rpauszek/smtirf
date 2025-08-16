import json
from collections import OrderedDict
from datetime import datetime

import numpy as np

from . import SMJsonEncoder


class SMTraceID:
    """
    lightweight class implementing unique Trace identifier
    coded by hex representation of recording time
    and index of spot within movie
    """

    def __init__(self, s):
        self.string = s

    @staticmethod
    def time2hex(dt):
        return hex(int(dt.timestamp()))[2:]  # trim 0x

    @classmethod
    def from_datetime(cls, dt, trcIndex=None):
        """instantiate from datetime object"""
        hxdt = SMTraceID.time2hex(dt)
        try:
            return cls(f"{hxdt}:{trcIndex:04d}")
        except (TypeError, ValueError):
            return cls(f"{hxdt}:XXXX")

    def new_trace(self, trcIndex):
        return self.__class__(f"{self.movID}:{trcIndex:04d}")

    def __str__(self):
        return self.string

    @property
    def movID(self):
        mov, _ = self.string.split(":")
        return mov

    @property
    def trcIndex(self):
        _, trc = self.string.split(":")
        return trc

    @property
    def isMovieID(self):
        return self.trcIndex == "XXXX"

    def strftime(self, fmt="%Y-%m-%d %H:%M:%S"):
        dt = datetime.fromtimestamp(int(self.movID, base=16))
        return dt.strftime(fmt)


class SMMovie:
    def __init__(self, movID, img, info):
        self._id = movID
        if img.ndim != 2:
            raise ValueError("image must be flat (not RGB channels)")
        self.img = img
        self.info = info

    def __str__(self):
        s = f"{self.__class__.__name__}\t{self._id}\n"
        for key, item in self.info.items():
            s += f"-> {key}\n\t{item}\n"
        s += "\n"
        return s


class SMMovieList(OrderedDict):
    def __init__(self):
        super().__init__(self)

    @classmethod
    def load(cls, images, movInfo):
        movies = cls()
        for item in movInfo:
            movies.append(item["id"], images[:, :, item["position"]], item["contents"])
        return movies

    def append(self, key, img, info):
        self[key] = SMMovie(key, img, info)

    def add_movie(self, key, mov):
        self[key] = mov

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:  # lookup by index
            keys = [k for k in self.keys()]
            return self[keys[key]]

    def _as_image_stack(self):
        """return stack of images (ndarray)"""
        images = [mov.img for j, (key, mov) in enumerate(self.items())]
        return np.stack(images, axis=2)

    def _as_json(self):
        """json-serialized list of info dicts"""
        return json.dumps(
            [
                {"id": str(mov._id), "position": j, "contents": mov.info}
                for j, (key, mov) in enumerate(self.items())
            ],
            cls=SMJsonEncoder,
        )


class SMSpotCoordinate:
    def __init__(self, coords):
        self._coords = coords

    def _as_dict(self):
        return self._coords


def where(condition):
    """
    Finds contiguous True regions of the boolean array "condition".
    Returns a 2D array where
      column 1 is the start index of the region
      column 2 is the end index.
    goo.gl/eExJV3
    """
    # Find the indices of changes in "condition"
    d = np.diff(condition)
    (idx,) = d.nonzero()
    # We need to start things after the change in "condition". Therefore,
    # we'll shift the index by 1 to the right.
    idx += 1
    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]
    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size]
    # Reshape the result into two columns
    idx.shape = (-1, 2)
    return idx
