"""Public package interface for yaplotlib."""

# even: stable; odd: develop
__version__ = "0.1.3"

from .core import (
    Line,
    Text,
    Circle,
    Arrow,
    Polygon,
    Color,
    SetPalette,
    Size,
    Layer,
    ArrowType,
    NewPage,
)
from .palettes import RandomPalettes, RainbowPalettes, GradationPalettes
from .frame import YaplotFrame, Yaplot
from .document import YaplotDocument

__all__ = [
    "__version__",
    "Line",
    "Text",
    "Circle",
    "Arrow",
    "Polygon",
    "Color",
    "SetPalette",
    "Size",
    "Layer",
    "ArrowType",
    "NewPage",
    "RandomPalettes",
    "RainbowPalettes",
    "GradationPalettes",
    "YaplotFrame",
    "Yaplot",
    "YaplotDocument",
]
