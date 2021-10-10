from pathlib import Path
from dataclasses import dataclass, field
import json


lib_path = Path(__file__).parent / "lib"


@dataclass
class PlotConfig:
    x_color: str = "#7A67EE"
    x_color_dim: str = "#BCD2EE"
    d_color: str = "#9ACD32"
    a_color: str = "#CD1076"
    i_color: str = "#8B8B83"
    line_width: float = 1
    zoom_span: dict = field(default_factory={})
    selection_span: dict = field(default_factory={})
    axes_dim_background: str = "#DEDEDE"

    @classmethod
    def from_json(cls, filename):
        with open(filename, "r") as J:
            return cls(**json.load(J))


class Config:

    def __init__(self):
        self.plot = PlotConfig.from_json(lib_path / "plot_config.json")


config = Config()
