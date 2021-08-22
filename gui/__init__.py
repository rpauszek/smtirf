from pathlib import Path
from dataclasses import dataclass
import json


@dataclass
class PlotConfig:
    x_color: str = "#7A67EE"
    d_color: str = "#9ACD32"
    a_color: str = "#CD1076"
    i_color: str = "#8B8B83"
    line_width: float = 1

    @classmethod
    def from_json(cls, filename):
        with open(filename, "r") as J:
            return cls(**json.load(J))


@dataclass
class Config:
    plot: PlotConfig


config = Config(PlotConfig.from_json(Path(__file__).parent / "lib/plot_config.json"))
