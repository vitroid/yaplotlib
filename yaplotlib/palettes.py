"""Palette helper functions for Yaplot."""

import colorsys
from typing import Sequence

from .core import SetPalette


def RandomPalettes(N: int, offset: int = 10) -> str:
    """黄金角に基づき、N 個のカラフルなパレットを自動生成する。"""
    omega = 2 / (5**0.5 - 1)
    s = ""
    for i in range(N):
        hue = (omega * i) % 1.0
        sat = 0.5
        bri = 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, sat, bri)
        s += SetPalette(i + offset, r, g, b, maxval=1.0)
    return s


def RainbowPalettes(N: int, offset: int = 10) -> str:
    """0..1 の等間隔な色相で虹色グラデーションのパレットを N 個生成する。"""
    s = ""
    for i in range(N):
        hue = i / N
        sat = 0.5
        bri = 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, sat, bri)
        s += SetPalette(i + offset, r, g, b, maxval=1.0)
    return s


def GradationPalettes(
    N: int,
    color: Sequence[float],
    color1: Sequence[float],
    offset: int = 10,
    maxval: float = 255.0,
) -> str:
    """color から color1 までの直線補間グラデーションパレットを N 個生成する。"""
    s = ""
    for i in range(N):
        ratio = i / (N - 1)
        r = color[0] * (1 - ratio) + color1[0] * ratio
        g = color[1] * (1 - ratio) + color1[1] * ratio
        b = color[2] * (1 - ratio) + color1[2] * ratio
        s += SetPalette(i + offset, r, g, b, maxval)
    return s
