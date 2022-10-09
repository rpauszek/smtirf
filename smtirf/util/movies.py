import numpy as np
import json
from collections import OrderedDict
from .json import SMJsonEncoder


class SMMovie():

    def __init__(self, movID, img, info):
        self._id = movID
        if img.ndim != 2:
            raise ValueError("image must be flat (not RGB channels)")
        self.img = img
        self.info = info

    def __str__(self):
        s = f"{self.__class__.__name__}\t{self._id}\n"
        for key, item in self.info.items():
            s += f"-> {key}\n\t{item}\n"
        s += "\n"
        return s


class SMMovieList(OrderedDict):

    def __init__(self):
        super().__init__(self)

    @classmethod
    def load(cls, images, movInfo):
        movies = cls()
        for item in movInfo:
            movies.append(item["id"], images[:,:,item["position"]], item["contents"])
        return movies

    def append(self, key, img, info):
        self[key] = SMMovie(key, img, info)

    def add_movie(self, key, mov):
        self[key] = mov

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError: # lookup by index
            keys = [k for k in self.keys()]
            return self[keys[key]]

    def _as_image_stack(self):
        """ return stack of images (ndarray) """
        images = [mov.img for j, (key, mov) in enumerate(self.items())]
        return np.stack(images, axis=2)

    def _as_json(self):
        """ json-serialized list of info dicts  """
        return json.dumps([{"id": str(mov._id), "position": j, "contents": mov.info}
                            for j, (key, mov) in enumerate(self.items())], cls=SMJsonEncoder)