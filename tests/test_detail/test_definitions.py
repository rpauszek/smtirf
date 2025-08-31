import numpy as np

from smtirf.detail.definitions import Coordinates


def test_coordinates():
    coord = Coordinates.from_array(np.array([1.2, 3.1, 5.1, 3.1]))
    assert coord.channel_1.x == 1.2
    assert coord.channel_1.y == 3.1
    assert coord.channel_2.x == 5.1
    assert coord.channel_2.y == 3.1


# todo: test json_default
