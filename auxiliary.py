# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> auxiliary
"""
from datetime import datetime
from collections import OrderedDict

class SMTraceID():
    """
        lightweight class implementing unique Trace identifier
        coded by hex representation of recording time
        and index of spot within movie
    """

    def __init__(self, s):
        self.string = s

    @staticmethod
    def time2hex(dt):
        return hex(int(dt.timestamp()))[2:] # trim 0x

    @classmethod
    def from_datetime(cls, dt, trcIndex=None):
        """ instantiate from datetime object """
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


class SMMovie():

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

    def append(self, key, img, info):
        self[key] = SMMovie(key, img, info)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError: # lookup by index
            keys = [k for k in self.keys()]
            return self[keys[key]]

class SMSpotCoordinate():

    def __init__(self, coords):
        self._coords = coords
