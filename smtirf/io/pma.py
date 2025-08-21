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
    donor_traces = data[:, 0::2].T
    acceptor_traces = data[:, 1::2].T
    return [RawTrace(d, a) for d, a in zip(donor_traces, acceptor_traces)]


def _read_pks(filename):
    """
    Read coordinates from .pks file and return in structured format.

    The file format is
        1      donor_1_x      donor_1_y      donor_1_background (?)
        2   acceptor_1_x   acceptor_1_y   acceptor_1_background (?)
        3      donor_2_x      donor_2_y      donor_2_background (?)
        4   acceptor_2_x   acceptor_2_y   acceptor_2_background (?)
    """
    with open(filename, "r") as file:
        data = np.loadtxt(file, dtype=float)[:, 1:-1]  # remove first and last columns
    return [Coordinates.from_array(line) for line in data.reshape((-1, 4))]


def _read_log(filename):
    Alias = namedtuple("Alias", ("name", "parser", "required"))
    msec_to_sec = lambda t: float(t) / 1000
    int_array = lambda s: [int(item) for item in s.split(" ")]

    KEY_ALIASES = {
        "filming_date_and_time": Alias(
            "timestamp", lambda s: datetime.strptime(s, "%a %b %d %H:%M:%S %Y"), True
        ),
        "server_index": Alias("server_index", int, False),
        "frame_resolution": Alias("frame_resolution", int_array, False),
        "background": Alias("background", int, True),
        "data_scaler": Alias("data_scaler", int, True),
        "byte_per_pixel": Alias("byte_per_pixel", int, False),
        "camera_information": Alias("camera", str, False),
        "camera_bit_depth": Alias("bit_depth", int, False),
        "gain": Alias("gain", int, True),
        "exposure_time_ms": Alias("exposure_time", msec_to_sec, True),
        "kinetic_cycle_time_ms": Alias("cycle_time", msec_to_sec, False),
        "lag_beetween_images_ms": Alias("lag_time", msec_to_sec, False),
        "active_area": Alias("active_area", int_array, False),
    }

    with open(filename, "r") as file:
        text = [
            stripped for line in file.readlines() if len(stripped := line.strip()) > 0
        ]

    keys = text[::2]
    parsed_keys = [re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_") for key in keys]
    values = text[1::2]

    # todo: remove unknown entries if empty
    log_dict = {"unknown_entries": {}}
    for key, value, original_key in zip(parsed_keys, values, keys):
        alias = KEY_ALIASES.get(key, None)
        if alias is None:
            warnings.warn(f'unknown entry "{original_key}" found in log.', stacklevel=3)
            log_dict["unknown_entries"][key] = value
            continue
        log_dict[alias.name] = alias.parser(value)

    # todo: message with original expected keys
    required_keys = [alias.name for alias in KEY_ALIASES.values() if alias.required]
    if missing_keys := sorted(required_keys - log_dict.keys()):
        raise KeyError(f"missing required keys: {", ".join(missing_keys)}.")

    return log_dict


def _read_tif(filename):
    image = imread(filename)
    return image if image.ndim == 2 else color.rgb2gray(image)
