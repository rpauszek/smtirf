from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class RawTrace:
    channel_1: np.ndarray
    channel_2: np.ndarray

    @property
    def n_frames(self):
        return len(self.channel_1)


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass
class Coordinates:
    """Peak coordinates for channel 1 (left) and channel 2 (right).

    Attributes
    ----------
    channel_1 : Point or None
        Coordinates of the spot in channel 1 (left-side).
    channel_2 : Point or None
        Coordinates of the spot in channel 2 (right-side).
    """

    channel_1: Optional[Point]
    channel_2: Optional[Point]

    @classmethod
    def from_array(cls, arr):
        """Create instance from array of floats.

        Parameters
        ----------
        arr: np.ndarray
            Array of coordinaetes in the form [ch1_x, ch1_y, ch2_x, ch2_y]
        """
        channel_1 = Point(*arr[:2])
        channel_2 = Point(*arr[2:])
        return cls(channel_1, channel_2)

    @classmethod
    def from_record_dict(cls, record):
        channel_1 = Point(record["ch1_x"], record["ch1_y"])
        channel_2 = Point(record["ch2_x"], record["ch2_y"])
        return cls(channel_1, channel_2)

    def as_list(self):
        return [self.channel_1.x, self.channel_1.y, self.channel_2.x, self.channel_2.y]


UNASSIGNED_CONFORMATIONAL_STATE = -1


@unique
class PhotophysicsEnum(Enum):
    SIGNAL = 0
    BLINK = 1
    BLEACH = 2


def json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
