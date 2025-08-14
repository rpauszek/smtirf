import numpy as np
import json
from importlib.metadata import version

__version__ = version("smtirf")

class SMJsonEncoder(json.JSONEncoder):
    """ https://bit.ly/2sb9YCT """
    def default(self, obj):
        try:
            return obj._as_dict()
        except AttributeError:
            pass

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, slice):
            return (obj.start, obj.stop)
        elif np.issubdtype(obj, np.signedinteger):
            return int(obj)
        elif np.issubdtype(obj, np.float):
            return float(obj)

        return json.JSONEncoder.default(self, obj)

class SMJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        for key, val in obj.items():
            if isinstance(val, list):
                obj[key] = np.array(val)
        return obj

from . import hmm
from . import util
from . import results
from .auxiliary import SMTraceID, SMMovieList, SMSpotCoordinate
from .auxiliary import where
from .hmm.models import HiddenMarkovModel
from .experiments import Experiment
