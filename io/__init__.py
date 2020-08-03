# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> io >> __init__
"""
from pathlib import Path
from . import pma
# from .experiments import *
from ..datamodel import experiments

# ==============================================================================
# EXPERIMENT FACTORY CLASS
# ==============================================================================
class Experiment():

    @staticmethod
    def from_pma(filename):
        filename = Path(filename)
        data = pma.read(filename.absolute())
        print(data["frameLength"])
