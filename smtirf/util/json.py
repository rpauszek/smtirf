import numpy as np
import json
from importlib import import_module


class SMJsonEncoder(json.JSONEncoder):
    """https://bit.ly/2sb9YCT"""

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
        elif np.issubdtype(obj, np.bool_):
            return bool(obj)

        return json.JSONEncoder.default(self, obj)


class SMJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "_class_name" in obj:
            module, cls_name = obj.pop("_class_name")
            cls = getattr(import_module(module), cls_name)
            return cls._from_json(**obj)

        for key, val in obj.items():
            if isinstance(val, list):
                obj[key] = np.array(val)

        return obj