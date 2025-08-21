from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class RawTrace:
    donor: np.ndarray
    acceptor: np.ndarray

    @property
    def n_frames(self):
        return len(self.donor)


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass
class Coordinates:
    """Donor/Acceptor peak coordinates.

    Attributes
    ----------
    donor : Point or None
        Coordinates of the donor spot.
    acceptor : Point or None
        Coordinates of the acceptor spot.
    """

    donor: Optional[Point]
    acceptor: Optional[Point]

    @classmethod
    def from_array(cls, arr):
        """Create instance from array of floats.

        Parameters
        ----------
        arr: np.ndarray
            Array of coordinaetes in the form [donor_x, donor_y, acceptor_x, acceptor_y]
        """
        donor = Point(*arr[:2])
        acceptor = Point(*arr[2:])
        return cls(donor, acceptor)

    def as_list(self):
        return [self.donor.x, self.donor.y, self.acceptor.x, self.acceptor.y]


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
