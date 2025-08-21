from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class MovieMetadata:
    n_traces: int
    n_frames: int
    src_filename: str
    timestamp: datetime
    ccd_gain: int
    data_scaler: Optional[int] = None
    log: Optional[dict] = field(default_factory=dict, repr=False)
