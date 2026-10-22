"""描画要素。

描画コマンドは種類表（:data:`yaplotlib.spec.KINDS`）で駆動する
:class:`Primitive` 1 種類にまとめる。パレット定義と SVG は、
描画コマンドとは出力位置も副作用も違うので別の型にする。
"""

import io
import operator
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import numpy as np

from .spec import KINDS, Kind

Point = tuple[float, float, float]
Rgb = tuple[int, int, int]

# 行頭（空白を除く）が '<' で始まり、<svg>...</svg> を含むこと。
_SVG_OPEN = re.compile(r"<svg\b", re.IGNORECASE)
_SVG_CLOSE = re.compile(r"</svg\s*>", re.IGNORECASE)


def _as_int(name: str, value: object, minimum: int) -> int:
    """bool を除く整数に変換し、minimum 以上であることを確かめる。"""
    if isinstance(value, bool):
        raise TypeError(f"{name} は整数で指定してください")
    try:
        number = operator.index(value)  # type: ignore[arg-type]
    except TypeError:
        raise TypeError(f"{name} は整数で指定してください") from None
    if number < minimum:
        raise ValueError(f"{name} は {minimum} 以上にしてください: {number}")
    return number


def _as_radius(value: object) -> float:
    if isinstance(value, bool):
        raise TypeError("radius は数値で指定してください")
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise TypeError("radius は数値で指定してください") from None
    if number < 0:
        raise ValueError(f"radius は 0 以上にしてください: {number}")
    return number


def _as_point(value: object) -> Point:
    try:
        x, y, z = value  # type: ignore[misc]
    except (TypeError, ValueError):
        raise ValueError(f"座標は x, y, z の 3 成分にしてください: {value!r}") from None
    return (float(x), float(y), float(z))


def _check_text(kind: str, text: Optional[str], required: bool) -> Optional[str]:
    if required:
        if not isinstance(text, str):
            raise TypeError(f"{kind} には文字列 text が必要です")
        if "\n" in text or "\r" in text:
            raise ValueError("text に改行は使えません")
        return text
    if text is not None:
        raise TypeError(f"{kind} は text を取りません")
    return None


@dataclass(frozen=True, slots=True)
class Primitive:
    """描画コマンド 1 つ。

    color を省略（None）すると、色のコマンドは出力されない。
    つまり直前の色を引き継ぐ。フレームの途中で色付きの要素より後ろに置くと、
    その色で描かれる。レイヤ・半径・矢印も同じで、None は「変えない」という意味。
    """

    kind: Kind
    points: tuple[Point, ...]
    text: Optional[str] = None
    layer: Optional[int] = None
    color: Optional[int] = None
    radius: Optional[float] = None
    arrow: Optional[int] = None

    def __post_init__(self) -> None:
        spec = KINDS.get(self.kind)
        if spec is None:
            known = ", ".join(KINDS)
            raise ValueError(f"未知の種類です: {self.kind!r}（{known}）")
        points = tuple(_as_point(p) for p in self.points)
        if spec.npoints is not None:
            if len(points) != spec.npoints:
                raise ValueError(
                    f"{self.kind} の座標は {spec.npoints} 個です（{len(points)} 個渡されました）"
                )
        elif len(points) < spec.min_points:
            raise ValueError(
                f"{self.kind} の座標は {spec.min_points} 個以上です"
                f"（{len(points)} 個渡されました）"
            )
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "text", _check_text(self.kind, self.text, spec.has_text))
        _apply_style(self)


def _apply_style(obj: object) -> None:
    layer = None if obj.layer is None else _as_int("layer", obj.layer, 1)  # type: ignore[attr-defined]
    color = None if obj.color is None else _as_int("color", obj.color, 0)  # type: ignore[attr-defined]
    radius = None if obj.radius is None else _as_radius(obj.radius)  # type: ignore[attr-defined]
    arrow = None if obj.arrow is None else _as_int("arrow", obj.arrow, 0)  # type: ignore[attr-defined]
    object.__setattr__(obj, "layer", layer)
    object.__setattr__(obj, "color", color)
    object.__setattr__(obj, "radius", radius)
    object.__setattr__(obj, "arrow", arrow)


def _empty(coords: object) -> bool:
    if isinstance(coords, np.ndarray):
        return coords.size == 0
    try:
        return len(coords) == 0  # type: ignore[arg-type]
    except TypeError:
        return False


def _as_rect(coords: object) -> Optional[np.ndarray]:
    """矩形の数値配列にできれば ndarray を返す。長さがまちまちなら None。"""
    try:
        array = np.asarray(coords, dtype=float)
    except (ValueError, TypeError):
        return None
    if array.dtype == object:
        return None
    return array


def _normalize_coords(kind: str, coords: object) -> Union[np.ndarray, tuple[np.ndarray, ...]]:
    """add_many の座標を (N, k, 3) の配列、または頂点数がまちまちな配列の列にする。"""
    spec = KINDS[kind]
    if _empty(coords):
        width = spec.npoints if spec.npoints is not None else spec.min_points
        return np.zeros((0, width, 3), dtype=float)

    array = _as_rect(coords)
    if array is None:
        if spec.npoints is not None:
            raise ValueError(
                f"{kind} の座標は形 (N, {spec.npoints}, 3) の配列にしてください"
            )
        return _ragged(kind, coords, spec.min_points)

    if spec.npoints == 1:
        if array.ndim == 2 and array.shape[1] == 3:
            array = array.reshape(array.shape[0], 1, 3)
        elif not (array.ndim == 3 and array.shape[1] == 1 and array.shape[2] == 3):
            raise ValueError(
                f"{kind} の座標は (N, 3) で渡してください（受け取った形は {array.shape}）"
            )
    elif spec.npoints is not None:
        if array.ndim != 3 or array.shape[2] != 3 or array.shape[1] != spec.npoints:
            hint = ""
            if array.ndim == 2:
                hint = (
                    " 2 次元配列は 1 個の要素なのか複数の点なのか区別できないので"
                    "受け付けません。1 個なら add を使ってください。"
                )
            raise ValueError(
                f"{kind} の座標は (N, {spec.npoints}, 3) で渡してください"
                f"（受け取った形は {array.shape}）。{hint}"
            )
    else:
        if array.ndim != 3 or array.shape[2] != 3 or array.shape[1] < spec.min_points:
            raise ValueError(
                f"{kind} の座標は (N, m, 3)（m >= {spec.min_points}）、"
                f"または頂点数がまちまちな配列の列にしてください"
                f"（受け取った形は {array.shape}）"
            )
    return np.array(array, dtype=float, copy=True)


def _ragged(kind: str, coords: object, min_points: int) -> tuple[np.ndarray, ...]:
    try:
        items = list(coords)  # type: ignore[arg-type]
    except TypeError:
        raise ValueError(f"{kind} の座標を読み取れません") from None
    arrays: list[np.ndarray] = []
    for item in items:
        array = np.asarray(item, dtype=float)
        if array.ndim != 2 or array.shape[1] != 3 or array.shape[0] < min_points:
            raise ValueError(
                f"{kind} の各要素は (m, 3)（m >= {min_points}）にしてください"
                f"（受け取った形は {array.shape}）"
            )
        arrays.append(np.array(array, dtype=float, copy=True))
    return tuple(arrays)


def _batch_count(coords: Union[np.ndarray, tuple[np.ndarray, ...]]) -> int:
    if isinstance(coords, np.ndarray):
        return int(coords.shape[0])
    return len(coords)


@dataclass(frozen=True, slots=True, eq=False)
class Batch:
    """同じ種類・同じスタイルの描画要素をまとめたもの。

    N 個の :class:`Primitive` には展開せず、座標は ndarray のまま保持する。
    座標の形は「要素数 N × 1 要素の座標数 k × 3」。

    - circle など座標 1 個の種類: ``(N, 3)``
    - line と stick: ``(N, 2, 3)``
    - polygon と polyline で頂点数がそろうとき: ``(N, m, 3)``
    - 頂点数がまちまちのとき: 形 ``(m_i, 3)`` の配列の列
    - text: ``(N, 3)`` と、長さ N の ``texts``
    """

    kind: Kind
    coords: Union[np.ndarray, tuple[np.ndarray, ...]]
    texts: Optional[tuple[str, ...]] = None
    layer: Optional[int] = None
    color: Optional[int] = None
    radius: Optional[float] = None
    arrow: Optional[int] = None

    def __post_init__(self) -> None:
        spec = KINDS.get(self.kind)
        if spec is None:
            known = ", ".join(KINDS)
            raise ValueError(f"未知の種類です: {self.kind!r}（{known}）")
        coords = _normalize_coords(self.kind, self.coords)
        count = _batch_count(coords)
        if spec.has_text:
            if self.texts is None:
                raise TypeError(f"{self.kind} には texts が必要です")
            texts = tuple(self.texts)
            if len(texts) != count:
                raise ValueError(
                    f"texts の長さ（{len(texts)}）が要素数（{count}）と一致しません"
                )
            for text in texts:
                _check_text(self.kind, text, True)
        elif self.texts is not None:
            raise TypeError(f"{self.kind} は texts を取りません")
        else:
            texts = None
        object.__setattr__(self, "coords", coords)
        object.__setattr__(self, "texts", texts)
        _apply_style(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Batch):
            return NotImplemented
        return (
            self.kind == other.kind
            and self.texts == other.texts
            and self.layer == other.layer
            and self.color == other.color
            and self.radius == other.radius
            and self.arrow == other.arrow
            and _coords_equal(self.coords, other.coords)
        )


def _coords_equal(
    a: Union[np.ndarray, tuple[np.ndarray, ...]],
    b: Union[np.ndarray, tuple[np.ndarray, ...]],
) -> bool:
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        return a.shape == b.shape and np.array_equal(a, b)
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
        return all(x.shape == y.shape and np.array_equal(x, y) for x, y in zip(a, b))
    return False


@dataclass(frozen=True, slots=True)
class PaletteDef:
    """パレット番号の色を定義する。

    出力される ``@ n r g b`` は、その番号の色を選ぶ副作用も持つ。
    """

    index: int
    rgb: Rgb

    def __post_init__(self) -> None:
        index = _as_int("palette", self.index, 0)
        try:
            red, green, blue = self.rgb
        except (TypeError, ValueError):
            raise ValueError(f"rgb は 3 成分にしてください: {self.rgb!r}") from None
        rgb = (
            _as_int("R", red, 0),
            _as_int("G", green, 0),
            _as_int("B", blue, 0),
        )
        for channel, name in zip(rgb, "RGB"):
            if channel > 255:
                raise ValueError(f"{name} は 0..255 にしてください: {channel}")
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "rgb", rgb)


@dataclass(frozen=True, slots=True)
class Svg:
    """画面に固定して重ねる SVG ブロック。

    空白を除いた先頭が ``<`` であり、``<svg>...</svg>`` を含むこと。
    自己終了の ``<svg/>`` は Yaplot が数えられないので受け付けない。
    """

    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", _validate_svg(self.text))

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Svg":
        """SVG ファイルを読み込む。"""
        return cls(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_figure(cls, fig: object) -> "Svg":
        """matplotlib の Figure を透明な SVG にする。"""
        buffer = io.StringIO()
        savefig = getattr(fig, "savefig", None)
        if savefig is None:
            raise TypeError("savefig を持つ Figure を渡してください")
        savefig(buffer, format="svg", transparent=True)
        return cls(buffer.getvalue())


def _validate_svg(text: object) -> str:
    if not isinstance(text, str):
        raise TypeError("SVG は文字列です")
    if not text.lstrip().startswith("<"):
        raise ValueError("SVG は '<' で始めてください")
    if _SVG_OPEN.search(text) is None or _SVG_CLOSE.search(text) is None:
        raise ValueError(
            "SVG には <svg>...</svg> が必要です。自己終了の <svg/> は使えません。"
        )
    return text


def coerce_svg(value: object) -> Svg:
    """文字列、ファイルパス、matplotlib の Figure、Svg のいずれかを Svg にする。"""
    if isinstance(value, Svg):
        return value
    if hasattr(value, "savefig"):
        return Svg.from_figure(value)
    if isinstance(value, Path):
        return Svg.from_file(value)
    if isinstance(value, str):
        if value.lstrip().startswith("<"):
            return Svg(value)
        return Svg.from_file(value)
    raise TypeError("SVG には文字列、パス、Figure、Svg のいずれかを渡してください")


@dataclass(frozen=True, slots=True)
class FrameBreak:
    """レガシー API の NewPage が入れるフレーム区切り。"""
