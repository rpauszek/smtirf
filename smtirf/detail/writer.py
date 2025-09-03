import json
from datetime import datetime

import h5py
import numpy as np

from smtirf import __version__ as current_version

from ..detail.definitions import (
    UNASSIGNED_CONFORMATIONAL_STATE,
    PhotophysicsEnum,
    json_default,
)
from ..detail.metadata import TRACE_DTYPE, TraceMetadata

SCHEMA_VERSION = "2.0.0"

DATASET_OPTS = dict(
    compression="gzip",
    compression_opts=5,
    shuffle=True,
    fletcher32=True,
)


def write_movie_to_hdf(
    savename,
    experiment_type,
    bleedthrough,
    gamma,
    traces,
    peaks,
    metadata,
    snapshot=None,
):
    """Write a movie to HDF5 from raw data import.

    To be called from helper functions in smtirf.io.import_dispatch

    Parameters
    ----------
    savename: Path
        file path to write HDF5
    experiment_type: {"fret"}
        experiment type, controls trace class
    bleedthrough: float
        fractional bleedthrough of channel 1 emission to channel 2
    gamma: float
        gamma correction
    traces: List[RawTrace]
        list of raw trace data
    peaks: List[Coordinates]
        peak localization coordinates
    metadata: MovieMetadata
        movie metadata
    snapshot: np.ndarray
        [H x W] movie snapshot image
    """

    with h5py.File(savename, "w") as hf:
        hf.attrs["smtirf_version"] = current_version
        hf.attrs["smtrc_version"] = SCHEMA_VERSION
        hf.attrs["date_modified"] = datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")
        hf.attrs["experiment_type"] = experiment_type
        hf.attrs["bleedthrough"] = bleedthrough
        hf.attrs["gamma"] = gamma

        mov_group = _initialize_movie(hf, metadata, snapshot)
        _write_trace_data(mov_group, metadata, traces)
        _write_default_statepaths(mov_group, metadata)
        _write_trace_metadata(mov_group, metadata, peaks)


def _initialize_movie(file_handle, metadata, snapshot):
    """Create a HDF group to store movie data.

    1. create group
    2. write movie metadata to attrs
    3. write trace index dataset (trace ids corresponding to rows in other datasets)

    Parameters
    ----------
    file_handle: h5py.File
        file handle to write data into
    metadata: MovieMetadata
        movie metadata
    snapshot: np.ndarray
        [H x W] movie snapshot image

    Returns
    -------
    h5py.Group:
        group to write movie data into
    """
    group = file_handle.create_group(f"movies/movie_{metadata.uid}")
    group.attrs.update(
        {
            "n_traces": metadata.n_traces,
            "n_frames": metadata.n_frames,
            "src_filename": metadata.src_filename,
            "timestamp": metadata.timestamp.isoformat(),
            "frame_length": metadata.frame_length,
            "ccd_gain": metadata.ccd_gain,
            # todo: store raw log, move conversion to datetime when constructing metadata
            "log": json.dumps(
                metadata.log,
                default=json_default,
                sort_keys=True,
                separators=(",", ":"),
            ),
        }
    )
    if metadata.data_scaler is not None:
        group.attrs["data_scaler"] = metadata.data_scaler

    trace_metadata = TraceMetadata.from_movie_metadata(metadata)
    trace_ids = np.array(
        [trace_metadata.make_trace_uid(i) for i in range(metadata.n_traces)],
        dtype="S32",
    )
    group.create_dataset(
        "trace_ids",
        data=trace_ids,
        dtype=h5py.string_dtype("ascii", length=32),  # fixed-length strings
    )

    if snapshot is not None:
        group.create_dataset(
            "snapshot",
            data=snapshot,
            dtype="uint8",
            chunks=snapshot.shape,
            **DATASET_OPTS,
        )

    return group


def _write_trace_data(group, movie_metadata, traces):
    """Write raw trace datasets.

    Parameters
    ----------
    group: h5py.Group
        movie group
    movie_metadata: MovieMetadata
        movie metadata
    traces: List[RawTrace]
        list of raw trace data
    """
    ch1_data = np.vstack([trace.channel_1 for trace in traces])
    ch2_data = np.vstack([trace.channel_2 for trace in traces])
    for name, data in zip(
        ("channel_1", "channel_2"), (ch1_data, ch2_data), strict=False
    ):
        group.create_dataset(
            f"traces/{name}",
            data=data,
            dtype="int16",
            chunks=(1, movie_metadata.n_frames),  # row-wise chunking
            **DATASET_OPTS,
        )


def _write_default_statepaths(group, movie_metadata):
    """Write trace statepath datasets with default values.

    Parameters
    ----------
    group: h5py.Group
        movie group
    movie_metadata: MovieMetadata
        movie metadata
    """
    for name, value, dtype in zip(
        ("photophysics", "conformation"),
        (PhotophysicsEnum.SIGNAL.value, UNASSIGNED_CONFORMATIONAL_STATE),
        (np.uint8, np.int8),
        strict=False,
    ):
        data = np.full(
            (movie_metadata.n_traces, movie_metadata.n_frames), value, dtype=dtype
        )
        group.create_dataset(
            f"statepaths/{name}",
            data=data,
            dtype=np.dtype(dtype).name,
            chunks=(1, movie_metadata.n_frames),  # row-wise chunking
            **DATASET_OPTS,
        )


def _write_trace_metadata(group, movie_metadata, peaks):
    """Write raw trace datasets.

    Stored as row records.

    Parameters
    ----------
    group: h5py.Group
        movie group
    movie_metadata: MovieMetadata
        movie metadata
    peaks: List[Coordinates]
        peak localization coordinates
    """

    trace_metadata = TraceMetadata.from_movie_metadata(movie_metadata)
    records = np.zeros(movie_metadata.n_traces, dtype=TRACE_DTYPE)

    for k, peak in enumerate(peaks):
        records[k] = trace_metadata.make_record(index=k, peak=peak)

    group.create_dataset(
        "traces/metadata", data=records, dtype=TRACE_DTYPE, **DATASET_OPTS
    )
