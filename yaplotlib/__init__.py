"""Yaplot 形式の描画データを作る。"""

# even: stable; odd: develop
__version__ = "1.0.1"

from .core import (
    Arrow,
    ArrowType,
    Circle,
    Color,
    Layer,
    Line,
    NewPage,
    Polygon,
    SetPalette,
    Size,
    Text,
)
from .document import YaplotDocument
from .elements import Batch, PaletteDef, Primitive, Svg
from .frame import Yaplot, YaplotFrame
from .globals import Globals
from .palettes import (
    GradationPalettes,
    RainbowPalettes,
    RandomPalettes,
    gradation_colors,
    rainbow_colors,
    random_colors,
)
from .spec import Kind

__all__ = [
    "__version__",
    "Kind",
    "Primitive",
    "Batch",
    "PaletteDef",
    "Svg",
    "Globals",
    "YaplotFrame",
    "Yaplot",
    "YaplotDocument",
    "random_colors",
    "rainbow_colors",
    "gradation_colors",
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
]
