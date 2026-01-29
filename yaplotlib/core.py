"""Low-level Yaplot command constructors."""

import colorsys
from typing import Iterable, Sequence, Optional, Union


def _plaintext(a: Sequence[float]) -> str:
    """座標やベクトルのシーケンスを Yaplot 形式のプレーンテキストに変換する（内部用）。"""
    s = ""
    for x in a:
        s += f"{x:.4f} "
    return s


def Line(v0: Sequence[float], v1: Sequence[float]) -> str:
    """2 点 v0, v1 を結ぶ線分を表す Yaplot コマンド文字列を返す。"""
    return "l " + _plaintext(v0) + _plaintext(v1) + "\n"


def Text(v: Sequence[float], txt: str) -> str:
    """位置 v に文字列 txt を描画する Yaplot コマンド文字列を返す。"""
    return "t " + _plaintext(v) + " " + txt + "\n"


def Circle(v0: Sequence[float]) -> str:
    """中心 v0 に円（点）を描画する Yaplot コマンド文字列を返す。"""
    return "c " + _plaintext(v0) + "\n"


def Arrow(v0: Sequence[float], v1: Sequence[float]) -> str:
    """始点 v0, 終点 v1 の矢印を描画する Yaplot コマンド文字列を返す。"""
    return "s " + _plaintext(v0) + _plaintext(v1) + "\n"


def Polygon(vertices: Iterable[Sequence[float]]) -> str:
    """頂点列 vertices から多角形を描画する Yaplot コマンド文字列を返す。"""
    verts = list(vertices)
    s = f"p {len(verts)} "
    for v in verts:
        s += _plaintext(v)
    return s + "\n"


def Color(x: int) -> str:
    """パレット番号 x の色を使用するコマンド文字列を返す。"""
    return f"@ {int(x)}\n"


def SetPalette(
    x: int,
    R: Union[int, Sequence[float]],
    G: Optional[float] = None,
    B: Optional[float] = None,
    maxval: float = 255.0,
) -> str:
    """パレット x の RGB 値を設定する Yaplot コマンド文字列を返す。

    R, G, B は 0..maxval の範囲の値、または (R, G, B) のシーケンスを与える。
    """
    if G is None:
        R, G, B = R  # type: ignore[misc]
    r = int(R * 255 / maxval)  # type: ignore[operator]
    g = int(G * 255 / maxval)  # type: ignore[operator]
    b = int(B * 255 / maxval)  # type: ignore[operator]
    return f"@ {int(x)} {r} {g} {b}\n"


def Size(x: float) -> str:
    """線や点のサイズ（太さ）を設定するコマンド文字列を返す。"""
    return f"r {float(x)}\n"


def Layer(x: int) -> str:
    """描画レイヤー番号を設定するコマンド文字列を返す。"""
    return f"y {int(x)}\n"


def ArrowType(x: int) -> str:
    """矢印のスタイル種別を設定するコマンド文字列を返す。"""
    return f"a {int(x)}\n"


def NewPage() -> str:
    """ページ区切り（フレーム区切り）を表すコマンド文字列を返す。"""
    return "\n"
