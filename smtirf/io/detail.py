from dataclasses import dataclass
from typing import Optional


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
