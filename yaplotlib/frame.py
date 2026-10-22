"""1 フレーム分の入れ物。

フレームは現在のスタイルを持たない。スタイルは各要素に付き、
省略した項目は書き出し時に「変えない」（global か Yaplot の既定）として扱われる。
"""

import warnings
from pathlib import Path
from typing import Iterable, Optional, Sequence, Union

from .elements import (
    Batch,
    FrameBreak,
    PaletteDef,
    Primitive,
    Svg,
    coerce_svg,
)
from .palettes import gradation_colors, rainbow_colors, random_colors
from .spec import Kind
from ._writer import render_frame

_Element = Union[Primitive, Batch, PaletteDef, FrameBreak]


def _deprecated(old: str, new: str) -> None:
    warnings.warn(
        f"{old} は非推奨です。{new} を使ってください。",
        DeprecationWarning,
        stacklevel=3,
    )


class YaplotFrame:
    """Yaplot の 1 フレーム。

    中身は :attr:`items`（描画要素とパレット定義）と :attr:`svgs` のリストで、
    どちらも直接操作してよい。

    ``color=None``（および layer, radius, arrow の None）は「その項目を出力しない」
    という意味で、直前の値を引き継ぐ。色を付けた要素の後ろに色なしの要素を置くと、
    前の色で描かれる。
    """

    def __init__(self) -> None:
        self.items: list[_Element] = []
        self.svgs: list[Svg] = []
        self._reset_legacy()

    def add(
        self,
        kind: Union[Kind, _Element],
        *points: Sequence[float],
        text: Optional[str] = None,
        layer: Optional[int] = None,
        color: Optional[int] = None,
        radius: Optional[float] = None,
        arrow: Optional[int] = None,
    ) -> _Element:
        """要素を 1 つ追加する。

        種類名と座標を渡すか、作成済みの要素を 1 つ渡す。座標は 1 点ずつ渡す。
        """
        if isinstance(kind, (Primitive, Batch, PaletteDef, FrameBreak)):
            if points or text is not None or any(
                value is not None for value in (layer, color, radius, arrow)
            ):
                raise TypeError("作成済みの要素に座標やスタイルは渡せません")
            self.items.append(kind)
            return kind
        prim = Primitive(
            kind,
            points,
            text=text,
            layer=layer,
            color=color,
            radius=radius,
            arrow=arrow,
        )
        self.items.append(prim)
        return prim

    def add_many(
        self,
        kind: Kind,
        coords: object,
        texts: Optional[Sequence[str]] = None,
        *,
        layer: Optional[int] = None,
        color: Optional[int] = None,
        radius: Optional[float] = None,
        arrow: Optional[int] = None,
    ) -> Batch:
        """同じ種類の要素をまとめて追加する。

        座標の形は「要素数 N × 1 要素の座標数 × 3」。
        line と stick は ``(N, 2, 3)``。始点と終点が別の配列なら
        ``np.stack([starts, ends], axis=1)`` で重ねる。
        座標 1 個の種類は ``(N, 3)``。text はそれに加えて長さ N の ``texts``。
        """
        batch = Batch(
            kind,
            coords,
            texts=None if texts is None else tuple(texts),
            layer=layer,
            color=color,
            radius=radius,
            arrow=arrow,
        )
        self.items.append(batch)
        return batch

    def palette(self, index: int, rgb: Sequence[int]) -> PaletteDef:
        """パレット番号の色を定義する。この番号が現在の色にもなる。"""
        item = PaletteDef(index, rgb)  # type: ignore[arg-type]
        self.items.append(item)
        return item

    def palettes(self, rgbs: Iterable[Sequence[int]], offset: int = 10) -> list[PaletteDef]:
        """色の列を、offset から順にパレットへ登録する。"""
        made: list[PaletteDef] = []
        for index, rgb in enumerate(rgbs):
            made.append(self.palette(index + offset, rgb))
        return made

    def add_svg(self, svg: object) -> Svg:
        """このフレームだけの SVG を追加する。

        文字列、ファイルパス、matplotlib の Figure、:class:`Svg` を受け付ける。
        """
        svg = coerce_svg(svg)
        self.svgs.append(svg)
        return svg

    def dumps(self, *, lower: bool = True) -> str:
        """このフレームだけをテキストにする。

        global ブロックは含まない。ファイル全体は :meth:`YaplotDocument.dumps` を使う。
        ``lower`` が真のとき、polyline は線分に分解して出力する。
        """
        return render_frame(self.items, self.svgs, None, lower)

    def save(self, path: Union[str, Path], *, lower: bool = True) -> None:
        """このフレームだけをファイルに書く。"""
        Path(path).write_text(self.dumps(lower=lower), encoding="utf-8")

    # 互換 API（非推奨）。Color() のあとに Line() と続ける書き方を再現するため、
    # ここだけ非公開のスタイルを持つ。-1 は「指定なし」。
    def _reset_legacy(self) -> None:
        self._leg_layer = 1
        self._leg_layer_set = False
        self._leg_color = 2
        self._leg_color_set = False
        self._leg_radius = 1.0
        self._leg_radius_set = False
        # Yaplot の矢印タイプの既定は 0。以前の実装は 1 と誤っていた。
        self._leg_arrow = 0
        self._leg_arrow_set = False

    def _style(self) -> dict[str, Union[int, float, None]]:
        return {
            "layer": self._leg_layer if self._leg_layer_set else None,
            "color": self._leg_color if self._leg_color_set else None,
            "radius": self._leg_radius if self._leg_radius_set else None,
            "arrow": self._leg_arrow if self._leg_arrow_set else None,
        }

    def _apply_overrides(self, layer: float = -1, color: float = -1, radius: float = -1, arrow: float = -1) -> None:
        if _given(layer) and layer != self._leg_layer:
            self._leg_layer = int(layer)
            self._leg_layer_set = True
        if _given(color) and color != self._leg_color:
            self._leg_color = int(color)
            self._leg_color_set = True
        if _given(radius) and radius != self._leg_radius:
            self._leg_radius = float(radius)
            self._leg_radius_set = True
        if _given(arrow) and arrow != self._leg_arrow:
            self._leg_arrow = int(arrow)
            self._leg_arrow_set = True

    def _remember_palette(self, index: int) -> None:
        # @ n r g b は現在の色も n にする。
        self._leg_color = int(index)
        self._leg_color_set = True

    def _add_palettes(self, colors: Sequence[Sequence[int]], offset: int) -> None:
        if not colors:
            return
        self.palettes(colors, offset)
        self._remember_palette(offset + len(colors) - 1)

    def Layer(self, layer: int, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Layer()", "要素の layer= か、global の layer")
        self._apply_overrides(layer=layer)

    def Color(self, color: int, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Color()", "要素の color=")
        self._apply_overrides(color=color)

    def Size(self, size: float, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Size()", "要素の radius=")
        self._apply_overrides(radius=size)

    def ArrowType(self, arrowtype: int, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.ArrowType()", "要素の arrow=")
        self._apply_overrides(arrow=arrowtype)

    def Line(self, a: Sequence[float], b: Sequence[float], layer: int = -1, color: int = -1, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Line()", "add('line', a, b)")
        self._apply_overrides(layer=layer, color=color)
        self.add("line", a, b, **self._style())

    def Arrow(
        self,
        a: Sequence[float],
        b: Sequence[float],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        arrowtype: int = -1,
        *,
        _quiet: bool = False,
    ) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Arrow()", "add('stick', a, b, arrow=...)")
        self._apply_overrides(layer=layer, color=color, radius=size, arrow=arrowtype)
        self.add("stick", a, b, **self._style())

    def Polygon(self, p: Iterable[Sequence[float]], layer: int = -1, color: int = -1, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Polygon()", "add('polygon', *vertices)")
        self._apply_overrides(layer=layer, color=color)
        self.add("polygon", *p, **self._style())

    def Circle(
        self,
        c: Sequence[float],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        *,
        _quiet: bool = False,
    ) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Circle()", "add('circle', center)")
        self._apply_overrides(layer=layer, color=color, radius=size)
        self.add("circle", c, **self._style())

    def SetPalette(
        self,
        x: int,
        R: Union[int, Sequence[float]],
        G: Optional[float] = None,
        B: Optional[float] = None,
        maxval: float = 255.0,
        *,
        _quiet: bool = False,
    ) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.SetPalette()", "palette(index, rgb)")
        if G is None:
            R, G, B = R  # type: ignore[misc]
        rgb = (
            int(R * 255 / maxval),  # type: ignore[operator]
            int(G * 255 / maxval),  # type: ignore[operator]
            int(B * 255 / maxval),  # type: ignore[operator]
        )
        self.palette(int(x), rgb)
        self._remember_palette(int(x))

    def GradationPalettes(
        self,
        N: int,
        color: Sequence[float],
        color1: Sequence[float],
        offset: int = 10,
        maxval: float = 255.0,
        *,
        _quiet: bool = False,
    ) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.GradationPalettes()", "palettes(gradation_colors(...))")
        self._add_palettes(gradation_colors(N, color, color1, maxval), offset)

    def RandomPalettes(self, N: int, offset: int = 10, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.RandomPalettes()", "palettes(random_colors(...))")
        self._add_palettes(random_colors(N), offset)

    def RainbowPalettes(self, N: int, offset: int = 10, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.RainbowPalettes()", "palettes(rainbow_colors(...))")
        self._add_palettes(rainbow_colors(N), offset)

    def NewPage(self, *, _quiet: bool = False) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.NewPage()", "YaplotDocument.new_frame()")
        self.items.append(FrameBreak())
        self._reset_legacy()

    def Points(
        self,
        points: Iterable[Sequence[float]],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        *,
        _quiet: bool = False,
    ) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.Points()", "add_many('circle', points)")
        self._apply_overrides(layer=layer, color=color, radius=size)
        style = self._style()
        for point in points:
            self.add("circle", point, **style)

    def LinesBatch(
        self,
        segments: Iterable[tuple[Sequence[float], Sequence[float]]],
        layer: int = -1,
        color: int = -1,
        *,
        _quiet: bool = False,
    ) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.LinesBatch()", "add_many('line', coords)")
        self._apply_overrides(layer=layer, color=color)
        style = self._style()
        for start, end in segments:
            self.add("line", start, end, **style)

    def ArrowsBatch(
        self,
        segments: Iterable[tuple[Sequence[float], Sequence[float]]],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        arrowtype: int = -1,
        *,
        _quiet: bool = False,
    ) -> None:
        if not _quiet:
            _deprecated("YaplotFrame.ArrowsBatch()", "add_many('stick', coords)")
        self._apply_overrides(layer=layer, color=color, radius=size, arrow=arrowtype)
        style = self._style()
        for start, end in segments:
            self.add("stick", start, end, **style)


def _given(value: float) -> bool:
    """レガシー API の -1（指定なし）と負値を除く。"""
    try:
        return value >= 0
    except TypeError:
        return False


# 互換用エイリアス（1 フレーム = 従来の Yaplot）
Yaplot = YaplotFrame
