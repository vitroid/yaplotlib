"""低レベル API。1 コマンドぶんの文字列を返す。

新しいコードでは :class:`yaplotlib.YaplotDocument` を使う。
これらの関数は互換のために残してある。
"""

import warnings
from typing import Iterable, Optional, Sequence, Union

from ._writer import format_command, format_palette
from .elements import Primitive


def _deprecated(name: str, replacement: str) -> None:
    warnings.warn(
        f"yaplotlib.{name}() は非推奨です。{replacement} を使ってください。",
        DeprecationWarning,
        stacklevel=3,
    )


def Line(v0: Sequence[float], v1: Sequence[float]) -> str:
    """2 点を結ぶ線分。非推奨。"""
    _deprecated("Line", "フレームの add('line', v0, v1)")
    prim = Primitive("line", (v0, v1))
    return format_command("l", prim.points)


def Text(v: Sequence[float], txt: str) -> str:
    """位置 v に文字列を描く。非推奨。"""
    _deprecated("Text", "フレームの add('text', v, text=...)")
    prim = Primitive("text", (v,), text=txt)
    return format_command("t", prim.points, text=prim.text)


def Circle(v0: Sequence[float]) -> str:
    """中心 v0 に円を描く。非推奨。"""
    _deprecated("Circle", "フレームの add('circle', v0)")
    prim = Primitive("circle", (v0,))
    return format_command("c", prim.points)


def Arrow(v0: Sequence[float], v1: Sequence[float]) -> str:
    """始点 v0、終点 v1 の棒（stick）を描く。非推奨。"""
    _deprecated("Arrow", "フレームの add('stick', v0, v1)")
    prim = Primitive("stick", (v0, v1))
    return format_command("s", prim.points)


def Polygon(vertices: Iterable[Sequence[float]]) -> str:
    """頂点列から多角形を描く。非推奨。"""
    _deprecated("Polygon", "フレームの add('polygon', *vertices)")
    prim = Primitive("polygon", tuple(vertices))
    return format_command("p", prim.points, count=True)


def Color(x: int) -> str:
    """パレット番号 x を選ぶ。非推奨。"""
    _deprecated("Color", "要素の color=")
    return f"@ {int(x)}\n"


def SetPalette(
    x: int,
    R: Union[int, Sequence[float]],
    G: Optional[float] = None,
    B: Optional[float] = None,
    maxval: float = 255.0,
) -> str:
    """パレット x の RGB を設定する。非推奨。

    R, G, B は 0..maxval の範囲、または (R, G, B) の列を渡す。
    """
    _deprecated("SetPalette", "フレームの palette(index, rgb)")
    if G is None:
        R, G, B = R  # type: ignore[misc]
    rgb = (
        int(R * 255 / maxval),  # type: ignore[operator]
        int(G * 255 / maxval),  # type: ignore[operator]
        int(B * 255 / maxval),  # type: ignore[operator]
    )
    return format_palette(int(x), rgb)


def Size(x: float) -> str:
    """円や棒の半径を設定する。非推奨。"""
    _deprecated("Size", "要素の radius=")
    return f"r {float(x)}\n"


def Layer(x: int) -> str:
    """描画レイヤを設定する。非推奨。"""
    _deprecated("Layer", "要素の layer=")
    return f"y {int(x)}\n"


def ArrowType(x: int) -> str:
    """矢印のスタイルを設定する。非推奨。"""
    _deprecated("ArrowType", "要素の arrow=")
    return f"a {int(x)}\n"


def NewPage() -> str:
    """フレームの区切り。非推奨。"""
    _deprecated("NewPage", "YaplotDocument.new_frame()")
    return "\n"
