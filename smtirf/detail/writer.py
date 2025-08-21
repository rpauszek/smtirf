import json

import h5py
import numpy as np

from smtirf import __version__ as current_version

from ..detail.definitions import (
    UNASSIGNED_CONFORMATIONAL_STATE,
    PhotophysicsEnum,
    json_default,
)

SCHEMA_VERSION = "2.0.0"


def write_movie_to_hdf(savename, traces, peaks, metadata, image=None):
    with h5py.File(savename, "w") as hf:
        hf.attrs["smtirf_version"] = current_version
        hf.attrs["smtrc_version"] = SCHEMA_VERSION

        mov_id = metadata.uid
        mov_group = hf.create_group(f"movies/movie_{mov_id}")
        mov_group.attrs["n_traces"] = metadata.n_traces
        mov_group.attrs["n_frames"] = metadata.n_frames
        mov_group.attrs["src_filename"] = metadata.src_filename
        mov_group.attrs["timestamp"] = metadata.timestamp.isoformat()
        mov_group.attrs["frame_length"] = metadata.frame_length
        mov_group.attrs["ccd_gain"] = metadata.ccd_gain
        if metadata.data_scaler is not None:
            mov_group.attrs["data_scaler"] = metadata.data_scaler
        # todo: store raw log, move conversion to datetime when constructing metadata
        mov_group.attrs["log"] = json.dumps(
            metadata.log, default=json_default, sort_keys=True, separators=(",", ":")
        )

        trace_ids = np.array(
            [f"{mov_id}_{i:04d}" for i in range(metadata.n_traces)], dtype="S32"
        )
        mov_group.create_dataset(
            "trace_ids",
            data=trace_ids,
            dtype=h5py.string_dtype("ascii", length=32),  # fixed-length strings
        )

        donor_data = np.vstack([trace.donor for trace in traces])
        acceptor_data = np.vstack([trace.acceptor for trace in traces])
        for name, data in zip(("donor", "acceptor"), (donor_data, acceptor_data)):
            mov_group.create_dataset(
                f"traces/{name}_traces",
                data=data,
                dtype="int16",
                compression="gzip",
                compression_opts=5,
                chunks=(1, metadata.n_frames),  # row-wise chunking
                shuffle=True,
                fletcher32=True,
            )

        for name, value, dtype in zip(
            ("photophysics", "conformation"),
            (PhotophysicsEnum.SIGNAL.value, UNASSIGNED_CONFORMATIONAL_STATE),
            (np.uint8, np.int8),
        ):
            data = np.full((metadata.n_traces, metadata.n_frames), value, dtype=dtype)
            mov_group.create_dataset(
                f"statepaths/{name}",
                data=data,
                dtype=np.dtype(dtype).name,
                compression="gzip",
                compression_opts=5,
                chunks=(1, metadata.n_frames),  # row-wise chunking
                shuffle=True,
                fletcher32=True,
            )

        trace_dtype = np.dtype(
            [
                ("trace_id", h5py.string_dtype("utf-8", length=32)),
                ("donor_x", np.float32),
                ("donor_y", np.float32),
                ("acceptor_x", np.float32),
                ("acceptor_y", np.float32),
                ("start", np.uint32),
                ("stop", np.uint32),
                ("donor_offset", np.float32),
                ("acceptor_offset", np.float32),
                ("is_selected", bool),
            ]
        )

        records = np.zeros(metadata.n_traces, dtype=trace_dtype)
        for k, (peak, trace_id) in enumerate(zip(peaks, trace_ids)):
            # todo: simplify, precompute last part and unpack peak; peak.as_list
            # todo: dataclass with index and peak None -> expose method record.make_default(idx, pk, n_frames)
            records[k] = (
                trace_id,
                peak.donor.x,
                peak.donor.y,
                peak.acceptor.x,
                peak.acceptor.y,
                0,
                metadata.n_frames,
                0,
                0,
                False,
            )

        mov_group.create_dataset(
            "traces/metadata",
            # shape=(n_traces,),
            data=records,
            dtype=trace_dtype,
            compression="gzip",
            compression_opts=5,
            shuffle=True,
            fletcher32=True,
        )
