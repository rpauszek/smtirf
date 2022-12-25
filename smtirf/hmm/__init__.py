import numpy as np


def row(x):
    x = np.atleast_1d(x)
    assert x.ndim == 1, "Cannot form a row vector from a 2D array."
    return x[np.newaxis, :]


def col(x):
    x = np.atleast_1d(x)
    assert x.ndim == 1, "Cannot form a column vector from a 2D array."
    return x[:, np.newaxis]
