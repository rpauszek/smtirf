# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> traces
"""
from abc import ABC, abstractmethod

# ==============================================================================
# BASE TRACE CLASSES
# ==============================================================================
class BaseTrace(ABC):

    def __init__(self, trcID, data, frameLength, pk, bleed, gamma):
        pass

    @property
    @abstractmethod
    def X(self):
        ...


# ==============================================================================
# Experiment Trace Subclasses
# ==============================================================================
class FretTrace(BaseTrace):

    @property
    def X(self):
        return 0


class PiecewiseTrace(BaseTrace):

    @property
    def X(self):
        return 1


class PifeTrace(BaseTrace):

    @property
    def X(self):
        return 2


class PifeCh2Trace(PifeTrace):

    @property
    def X(self):
        return 3


class MultimerTrace(BaseTrace):

    @property
    def X(self):
        return 4
