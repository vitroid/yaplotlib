"""パレットの色を作る。

:func:`random_colors` などは 0..255 の RGB のリストを返す。
文字列を返す ``RandomPalettes`` などは、互換のために残してある。
"""

import colorsys
from typing import Sequence

from ._writer import format_palette

Rgb = tuple[int, int, int]


def _channel(value: float) -> int:
    return int(value * 255)


def random_colors(n: int) -> list[Rgb]:
    """黄金角でずらした、彩度 0.5 の色を n 個返す。"""
    omega = 2 / (5**0.5 - 1)
    colors: list[Rgb] = []
    for i in range(n):
        hue = (omega * i) % 1.0
        red, green, blue = colorsys.hsv_to_rgb(hue, 0.5, 1.0)
        colors.append((_channel(red), _channel(green), _channel(blue)))
    return colors


def rainbow_colors(n: int) -> list[Rgb]:
    """色相を等間隔に取った虹色を n 個返す。"""
    colors: list[Rgb] = []
    for i in range(n):
        hue = i / n if n else 0.0
        red, green, blue = colorsys.hsv_to_rgb(hue, 0.5, 1.0)
        colors.append((_channel(red), _channel(green), _channel(blue)))
    return colors


def gradation_colors(
    n: int,
    color: Sequence[float],
    color1: Sequence[float],
    maxval: float = 255.0,
) -> list[Rgb]:
    """color から color1 までを n 個に直線補間し、0..255 の RGB にする。"""
    if n < 1:
        return []
    colors: list[Rgb] = []
    for i in range(n):
        ratio = 0.0 if n == 1 else i / (n - 1)
        red = color[0] * (1 - ratio) + color1[0] * ratio
        green = color[1] * (1 - ratio) + color1[1] * ratio
        blue = color[2] * (1 - ratio) + color1[2] * ratio
        colors.append(
            (
                int(red * 255 / maxval),
                int(green * 255 / maxval),
                int(blue * 255 / maxval),
            )
        )
    return colors


def _commands(colors: Sequence[Rgb], offset: int) -> str:
    return "".join(format_palette(index + offset, rgb) for index, rgb in enumerate(colors))


def RandomPalettes(N: int, offset: int = 10) -> str:
    """黄金角に基づくパレット定義のコマンド文字列を返す。"""
    return _commands(random_colors(N), offset)


def RainbowPalettes(N: int, offset: int = 10) -> str:
    """虹色パレット定義のコマンド文字列を返す。"""
    return _commands(rainbow_colors(N), offset)


def GradationPalettes(
    N: int,
    color: Sequence[float],
    color1: Sequence[float],
    offset: int = 10,
    maxval: float = 255.0,
) -> str:
    """グラデーションパレット定義のコマンド文字列を返す。"""
    return _commands(gradation_colors(N, color, color1, maxval), offset)
