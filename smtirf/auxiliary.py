# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> auxiliary
"""
import numpy as np






# ==============================================================================
# functions
# ==============================================================================
def where(condition):
    """
    Finds contiguous True regions of the boolean array "condition".
    Returns a 2D array where
      column 1 is the start index of the region
      column 2 is the end index.
    goo.gl/eExJV3
    """
    # Find the indices of changes in "condition"
    d = np.diff(condition)
    idx, = d.nonzero()
    # We need to start things after the change in "condition". Therefore,
    # we'll shift the index by 1 to the right.
    idx += 1
    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]
    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size]
    # Reshape the result into two columns
    idx.shape = (-1,2)
    return idx
