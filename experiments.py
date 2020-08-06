# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
smtirf >> experiments
"""
import numpy as np
from pathlib import Path
from datetime import datetime
import h5py, json
import smtirf
from . import SMTraceID, SMMovieList
from . import SMJsonDecoder, SMJsonEncoder
from . import traces
from . import io

# ==============================================================================
# BASE EXPERIMENT CLASS
# ==============================================================================
class BaseExperiment():

    def __init__(self, movies, traces, frameLength, comments=""):
        self._movies = movies
        self._traces = traces
        self.frameLength = frameLength
        self.comments = comments

    def save(self, savename):
        Experiment.write_to_hdf(savename, self)

    # ==========================================================================
    # sequence interface
    # ==========================================================================
    def __getitem__(self, index):
        return self._traces[index]

    def __len__(self):
        return len(self._traces)

    def __str__(self):
        return f"{self.__class__.__name__}\t{self.nSelected}/{len(self)} selected"

    # ==========================================================================
    # properties
    # ==========================================================================
    @property
    def nSelected(self):
        return sum(1 for trc in self if trc.isSelected)



# ==============================================================================
# Experiment Concrete Subclasses
# ==============================================================================
class FretExperiment(BaseExperiment):
    traceClass = traces.FretTrace
    classLabel = "fret"

class PiecewiseExperiment(BaseExperiment):
    traceClass = traces.PiecewiseTrace
    classLabel = "piecewise"

class PifeExperiment(BaseExperiment):
    traceClass = traces.PifeTrace
    classLabel = "pife"

class PifeCh2Experiment(BaseExperiment):
    traceClass = traces.PifeCh2Trace
    classLabel = "pife2"

class MultimerExperiment(BaseExperiment):
    traceClass = traces.MultimerTrace
    classLabel = "multimer"



# ==============================================================================
# EXPERIMENT FACTORY CLASS
# ==============================================================================
class Experiment():

    CLASS_TYPES = {"fret": FretExperiment,
                   "piecewise": PiecewiseExperiment,
                   "pife": PifeExperiment,
                   "pife2": PifeCh2Experiment,
                   "multimer": MultimerExperiment}

    @staticmethod
    def build(cls, D0, A0, S0, SP, pks, recordTime, frameLength,
                          info, img, bleed, gamma, comments=""):

        movID = SMTraceID.from_datetime(recordTime)
        movies = SMMovieList()
        movies.append(movID, img, info)

        traces = [cls.traceClass(movID.new_trace(j), np.vstack((d, a, s0, sp)),
                                 frameLength, pk=pk, bleed=bleed, gamma=gamma)
                  for j, (d, a, s0, sp, pk) in enumerate(zip(D0, A0, S0, SP, pks))]
        return cls(movies, traces, frameLength, comments)

    @staticmethod
    def from_pma(filename, experimentType, bleed=0.05, gamma=1, comments=""):
        filename = Path(filename)
        data = io.pma.read(filename.absolute())
        cls = Experiment.CLASS_TYPES[experimentType.lower()]
        return Experiment.build(cls, bleed=bleed, gamma=gamma, comments=comments, **data)

    @staticmethod
    def write_to_hdf(filename, experiment):
        filename = Path(filename).absolute()
        with h5py.File(filename, "w") as HF:
            # store Experiment -------------------------------------------------
            HF.attrs["experimentType"] = experiment.classLabel
            HF.attrs["frameLength"] = experiment.frameLength
            HF.attrs["comments"] = experiment.comments

            # store MovieList --------------------------------------------------
            # images, movInfo = experiment._movies.serialize()
            dataset = HF.create_dataset("movies", data=experiment._movies._as_image_stack(), compression="gzip")
            dataset.attrs["movies"] = json.dumps(experiment._movies._as_json(), cls=SMJsonEncoder)

            # store Traces -----------------------------------------------------
            traceGroup = HF.create_group("traces")
            for trc in experiment:
                # data, props, model = trc.serialize()
                dataset = traceGroup.create_dataset(str(trc._id), data=trc._raw_data, compression="gzip")
                dataset.attrs["properties"] = json.dumps(trc._as_json(), cls=SMJsonEncoder)
                try:
                    dataset.attrs["model"] = json.dumps(trc.model._as_json(), cls=SMJsonEncoder)
                except AttributeError:
                    pass

            # store auxiliary attributes ---------------------------------------
            HF.attrs["nTraces"] = len(experiment)
            HF.attrs["nSelected"] = experiment.nSelected
            HF.attrs["dateModified"] = datetime.now().strftime("%a %b %d, %Y\t%H:%M:%S")
            HF.attrs["version"] = smtirf.__version__

    @staticmethod
    def load(filename):
        filename = Path(filename).absolute()
        print(filename)
        with h5py.File(filename, "r") as HF:
            # load Experiment --------------------------------------------------
            cls = Experiment.CLASS_TYPES[HF.attrs["experimentType"]]
            frameLength = HF.attrs["frameLength"]
            comments = HF.attrs["comments"]

            # load MovieList ---------------------------------------------------
            images = HF["movies"][:]
            movInfo = json.loads(HF["movies"].attrs["movies"])
            if isinstance(movInfo, dict): # re-format if < v0.1.3
                tmp = [None] * len(movInfo)
                for key, item in movInfo.items():
                    pos = item.pop("position")
                    d = {"id": key+":XXXX", "position": pos, "contents": item}
                    tmp[pos] = d
                movInfo = tmp
            movies = SMMovieList()
            for item in movInfo:
                movies.append(item["id"], images[item["position"]], item["contents"])

            # load Traces ------------------------------------------------------
            traces = []
            for key, item in HF["traces"].items():
                _id = SMTraceID(key)
                try:
                    model = json.loads(item.attrs["model"], cls=SMJsonDecoder)
                except KeyError:
                    model = None
                props = json.loads(item.attrs["properties"], cls=SMJsonDecoder)
                traces.append(cls.traceClass(_id, item[:], model=model, **props))

            return cls(movies, traces, frameLength, comments)

        # @staticmethod
        # def load(filename):
        #     filename = os.path.abspath(filename)
        #     with h5py.File(filename, "r") as HF:
        #         cls = Experiment._CLASS_TYPES[HF.attrs["experimentType"]]
        #         frameLength = HF.attrs["frameLength"]
        #         comments = HF.attrs["comments"]
        #         movies = smtirf.data.MovieList.from_hdf(HF["movies"])
        #         traces = [cls.traceClass.from_hdf(key,item) for key, item in HF["traces"].items()]
        #     return cls(movies, traces, frameLength, comments)
