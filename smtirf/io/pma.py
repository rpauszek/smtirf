import re
import warnings
from collections import namedtuple
from datetime import datetime

import numpy as np
from skimage import color
from skimage.io import imread

from ..detail.definitions import Coordinates, RawTrace


def _read_traces(filename):
    with open(filename.with_suffix(".traces"), "rb") as F:
        n_frames = np.fromfile(F, dtype=np.int32, count=1)[0]
        n_records = np.fromfile(F, dtype=np.int16, count=1)[0]
        # check number of traces is integer
        if (n_records % 1) != 0:
            raise ValueError(f"non-integer number of traces in dataset [{n_records}]")

        # read data, records as columns
        data = np.fromfile(F, dtype=np.int16, count=-1).reshape(
            (n_frames, n_records), order="C"
        )

    # split channels, traces as rows
    ch1_traces = data[:, 0::2].T
    ch2_traces = data[:, 1::2].T
    return [RawTrace(d, a) for d, a in zip(ch1_traces, ch2_traces)]


def _read_pks(filename):
    """
    Read coordinates from .pks file and return in structured format.

    The file format is
        1   ch1_1_x   ch1_1_y   ch1_1_background (?)
        2   ch2_1_x   ch2_1_y   ch2_1_background (?)
        3   ch1_2_x   ch1_2_y   ch1_2_background (?)
        4   ch2_2_x   ch2_2_y   ch2_2_background (?)
    """
    with open(filename, "r") as file:
        data = np.loadtxt(file, dtype=float)[:, 1:-1]  # remove first and last columns
    return [Coordinates.from_array(line) for line in data.reshape((-1, 4))]


def _read_log(filename):
    EntryInfo = namedtuple("EntryInfo", ("expected_key", "parser", "required"))
    msec_to_sec = lambda t: float(t) / 1000
    int_array = lambda s: [int(item) for item in s.split(" ")]

    EXPECTED_ENTRIES = {
        "filming_date_and_time": EntryInfo(
            "Filming Date and Time",
            lambda s: datetime.strptime(s, "%a %b %d %H:%M:%S %Y"),
            True,
        ),
        "server_index": EntryInfo("Server Index", int, False),
        "frame_resolution": EntryInfo("Frame Resolution", int_array, False),
        "background": EntryInfo("Background", int, True),
        "data_scaler": EntryInfo("Data Scaler", int, True),
        "byte_per_pixel": EntryInfo("Byte Per Pixel", int, False),
        "camera_information": EntryInfo("Camera Information", str, False),
        "camera_bit_depth": EntryInfo("Camera Bit Depth", int, False),
        "gain": EntryInfo("Gain", int, True),
        "exposure_time_ms": EntryInfo("Exposure Time [ms]", msec_to_sec, True),
        "kinetic_cycle_time_ms": EntryInfo(
            "Kinetic Cycle Time [ms]", msec_to_sec, False
        ),
        "lag_beetween_images_ms": EntryInfo(
            "Lag Beetween Images	[ms]", msec_to_sec, False
        ),
        "active_area": EntryInfo("Active Area", int_array, False),
    }

    with open(filename, "r") as file:
        text = [
            stripped for line in file.readlines() if len(stripped := line.strip()) > 0
        ]

    keys = text[::2]
    parsed_keys = [re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_") for key in keys]
    values = text[1::2]

    log_dict = {"unknown_entries": {}}
    for parsed_key, value, original_key in zip(parsed_keys, values, keys):
        entry = EXPECTED_ENTRIES.get(parsed_key, None)
        if entry is None:
            warnings.warn(f'unknown entry "{original_key}" found in log.', stacklevel=3)
            log_dict["unknown_entries"][parsed_key] = value
            continue
        log_dict[parsed_key] = entry.parser(value)
    if len(log_dict["unknown_entries"]) == 0:
        log_dict.pop("unknown_entries")

    required_keys = {
        parsed_key for parsed_key, entry in EXPECTED_ENTRIES.items() if entry.required
    }
    if missing := required_keys - log_dict.keys():
        missing_original_keys = [
            EXPECTED_ENTRIES[key].expected_key for key in sorted(missing)
        ]
        raise KeyError(f"missing required entries: {", ".join(missing_original_keys)}.")

    return log_dict


def _read_tif(filename):
    snapshot = imread(filename)
    return snapshot if snapshot.ndim == 2 else color.rgb2gray(snapshot)
