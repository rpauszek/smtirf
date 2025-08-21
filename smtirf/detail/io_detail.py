from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class RawTrace:
    donor: np.ndarray
    acceptor: np.ndarray

    @property
    def n_frames(self):
        return len(self.donor)

    @property
    def signal_statepath(self):
        return np.full(self.n_frames, 0)

    @property
    def statepath(self):
        return np.full(self.n_frames, -1)


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
