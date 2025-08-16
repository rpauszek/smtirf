import numpy as np

from smtirf.io.detail import Coordinates


def test_coordinates():
    coord = Coordinates.from_array(np.array([1.2, 3.1, 5.1, 3.1]))
    assert coord.donor.x == 1.2
    assert coord.donor.y == 3.1
    assert coord.acceptor.x == 5.1
    assert coord.acceptor.y == 3.1
