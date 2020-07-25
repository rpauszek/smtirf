# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> datamodel >> __init__
"""
from datetime import datetime

# ==============================================================================
class SMTraceID():
    """
        lightweight class implementing unique Trace identifier
        coded by hex representation of recording time
        and index of spot within movie
    """

    def __init__(self, s):
        self.string = s

    @classmethod
    def from_datetime(cls, dt, trcIndex=None):
        """ instantiate from datetime object """
        hxdt = hex(int(dt.timestamp()))[2:] # trim 0x
        try:
            return cls(f"{hxdt}:{trcIndex:04d}")
        except (TypeError, ValueError):
            return cls(f"{hxdt}:XXXX")

    def __str__(self):
        return self.string

    @property
    def movID(self):
        mov, trc = self.string.split(":")
        return mov

    @property
    def trcIndex(self):
        mov, trc = self.string.split(":")
        return trc

    def strftime(self, fmt="%Y-%m-%d %H:%M:%S"):
        dt = datetime.fromtimestamp(int(self.movID, base=16))
        return dt.strftime(fmt)

# ==============================================================================
