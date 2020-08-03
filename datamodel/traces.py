# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> datamodel >> traces
"""
from abc import ABC, abstractmethod

class BaseTrace(ABC):

    def __init__(self):
        pass

    @property
    @abstractmethod
    def X(self):
        ...
