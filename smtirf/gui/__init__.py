from pathlib import Path
from dataclasses import dataclass, field
import json


lib_path = Path(__file__).parent / "lib"


@dataclass
class Colors:
    selected: str = "#7A67EE"
    selected_dim: str = "#BCD2EE"
    donor: str = "#9ACD32"
    acceptor: str = "#CD1076"
    total: str = "#8B8B83"
    fit: str = "#000000"
    dim_background: str = "#DEDEDE"


@dataclass
class LineWidths:
    default: float = 1
    fit: float = 2


@dataclass
class Spans:
    zoom: dict = field(default_factory={})
    selection: dict = field(default_factory={})
    baseline: dict = field(default_factory={})


class Config:
    def __init__(self):
        with open(lib_path / "plot_config.json", "r") as J:
            config_dict = json.load(J)

        self.colors = Colors(**config_dict["colors"])
        self.linewidths = LineWidths(**config_dict["line_widths"])
        self.spans = Spans(**config_dict["spans"])


config = Config()
