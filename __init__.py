# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> __init__
"""

__version__ = "0.1.3"
print(f"smtirf v{__version__}")

from datetime import datetime

# ==============================================================================
# AUXILIARY CLASSES
# ==============================================================================
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


class Movie():

    def __init__(self):
        pass

# ==============================================================================
# PACKAGE IMPORTS
# ==============================================================================
from .io import Experiment
