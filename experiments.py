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

    # ==========================================================================
    # instance methods
    # ==========================================================================
    def detect_baseline(self, baselineCutoff=100, nComponents=5, nPoints=1e4,
                        maxIter=50, tol=1e-3, printWarnings=False,
                        where="first", correctOffsets=True):
        M = smtirf.util.AutoBaselineModel(self, baselineCutoff=baselineCutoff)
        M.train_gmm(nComponents=nComponents, nPoints=nPoints)
        M.train_hmm(maxIter=maxIter, tol=tol, printWarnings=printWarnings)
        for trc, sp in zip(self, M.SP):
            trc.set_signal_labels(sp, where=where, correctOffsets=correctOffsets)



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
            dataset = HF.create_dataset("movies", data=experiment._movies._as_image_stack(), compression="gzip")
            dataset.attrs["movies"] = experiment._movies._as_json()

            # store Traces -----------------------------------------------------
            traceGroup = HF.create_group("traces")
            for trc in experiment:
                dataset = traceGroup.create_dataset(str(trc._id), data=trc._raw_data, compression="gzip")
                dataset.attrs["properties"] = trc._as_json()
                try:
                    dataset.attrs["model"] = json.dumps(trc.model._as_json(), cls=SMJsonEncoder)
                except AttributeError: # model is None
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
            movies = SMMovieList().load(images, movInfo)

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

    @staticmethod
    def merge(filenames, selectedOnly=True):
        filenames = [Path(filename).absolute() for filename in filenames]
        # check that types are compatible
        frameLength, experimentType = Experiment._check_file_compatibility(filenames)
        # aggregate data
        movies = SMMovieList()
        traces = []
        for filename in filenames:
            e = Experiment.load(filename)
            tmpMovies = {key: mov for key, mov in e._movies.items()}
            if selectedOnly:
                tmpTraces = [trc for trc in e if trc.isSelected]
                tmpIds = set([f"{trc.movID}:XXXX" for trc in e if trc.isSelected])
            else:
                tmpTraces = [trc for trc in e]
                tmpIds = set([f"{trc.movID}:XXXX" for trc in e])
            traces.extend(tmpTraces)
            for key, mov in e._movies.items():
                if key in tmpIds:
                    movies.add_movie(key, mov)
        if len(traces) == 0:
            raise ValueError("No traces selected")
        cls = Experiment.CLASS_TYPES[experimentType]
        return cls(movies, traces, frameLength)

    @staticmethod
    def _check_file_compatibility(filenames):
        frameLengths = set()
        experimentTypes = set()
        for filename in filenames:
            with h5py.File(filename, "r") as HF:
                frameLengths.add(HF.attrs["frameLength"])
                experimentTypes.add(HF.attrs["experimentType"])
        if not len(frameLengths)==1:
            raise ValueError("Integration times are not compatible for all files")
        if not len(experimentTypes)==1:
            raise ValueError("Experiment types are not compatible for all files")
        return frameLengths.pop(), experimentTypes.pop()
