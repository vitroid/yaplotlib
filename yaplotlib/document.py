"""複数フレームと global ブロックからなる Yaplot ドキュメント。"""

from pathlib import Path
from typing import Iterable, Iterator, Optional, Sequence, Union

from ._writer import render_document
from .frame import YaplotFrame, _deprecated
from .globals import Globals


class YaplotDocument:
    """Yaplot のファイル 1 つ。

    :attr:`globals` に全フレーム共通の既定値と SVG を置き、
    :meth:`new_frame` が返すフレームに描画要素を追加する。
    """

    def __init__(self) -> None:
        self.globals = Globals()
        self.frames: list[YaplotFrame] = []

    def new_frame(self) -> YaplotFrame:
        """フレームを 1 つ追加して、それを返す。"""
        frame = YaplotFrame()
        self.frames.append(frame)
        return frame

    @property
    def current(self) -> YaplotFrame:
        """最後に追加したフレームを返す。"""
        if not self.frames:
            raise IndexError("フレームがありません。new_frame() を先に呼んでください。")
        return self.frames[-1]

    def __iter__(self) -> Iterator[YaplotFrame]:
        return iter(self.frames)

    def __len__(self) -> int:
        return len(self.frames)

    def dumps(self, *, lower: bool = True) -> str:
        """global ブロックと全フレームをテキストにする。

        ``lower`` が真のとき、polyline は線分に分解して出力する。
        """
        return render_document(self.globals, self.frames, lower)

    def save(self, path: Union[str, Path], *, lower: bool = True) -> None:
        """ドキュメント全体をファイルに書く。"""
        Path(path).write_text(self.dumps(lower=lower), encoding="utf-8")

    def _legacy_frame(self) -> YaplotFrame:
        if not self.frames:
            return self.new_frame()
        return self.frames[-1]

    # 互換 API（非推奨）。呼ばれた時点でフレームが無ければ 1 つ作る。
    def Layer(self, layer: int) -> None:
        _deprecated("YaplotDocument.Layer()", "要素の layer= か、global の layer")
        self._legacy_frame().Layer(layer, _quiet=True)

    def Color(self, color: int) -> None:
        _deprecated("YaplotDocument.Color()", "要素の color=")
        self._legacy_frame().Color(color, _quiet=True)

    def Size(self, size: float) -> None:
        _deprecated("YaplotDocument.Size()", "要素の radius=")
        self._legacy_frame().Size(size, _quiet=True)

    def ArrowType(self, arrowtype: int) -> None:
        _deprecated("YaplotDocument.ArrowType()", "要素の arrow=")
        self._legacy_frame().ArrowType(arrowtype, _quiet=True)

    def Line(self, a: Sequence[float], b: Sequence[float], layer: int = -1, color: int = -1) -> None:
        _deprecated("YaplotDocument.Line()", "フレームの add('line', a, b)")
        self._legacy_frame().Line(a, b, layer, color, _quiet=True)

    def Arrow(
        self,
        a: Sequence[float],
        b: Sequence[float],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        arrowtype: int = -1,
    ) -> None:
        _deprecated("YaplotDocument.Arrow()", "フレームの add('stick', a, b, arrow=...)")
        self._legacy_frame().Arrow(a, b, layer, color, size, arrowtype, _quiet=True)

    def Polygon(self, p: Iterable[Sequence[float]], layer: int = -1, color: int = -1) -> None:
        _deprecated("YaplotDocument.Polygon()", "フレームの add('polygon', *vertices)")
        self._legacy_frame().Polygon(p, layer, color, _quiet=True)

    def Circle(
        self,
        c: Sequence[float],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
    ) -> None:
        _deprecated("YaplotDocument.Circle()", "フレームの add('circle', center)")
        self._legacy_frame().Circle(c, layer, color, size, _quiet=True)

    def SetPalette(
        self,
        x: int,
        R: Union[int, Sequence[float]],
        G: Optional[float] = None,
        B: Optional[float] = None,
        maxval: float = 255.0,
    ) -> None:
        _deprecated("YaplotDocument.SetPalette()", "フレームの palette(index, rgb)")
        self._legacy_frame().SetPalette(x, R, G, B, maxval, _quiet=True)

    def GradationPalettes(
        self,
        N: int,
        color: Sequence[float],
        color1: Sequence[float],
        offset: int = 10,
        maxval: float = 255.0,
    ) -> None:
        _deprecated("YaplotDocument.GradationPalettes()", "フレームの palettes(gradation_colors(...))")
        self._legacy_frame().GradationPalettes(N, color, color1, offset, maxval, _quiet=True)

    def RandomPalettes(self, N: int, offset: int = 10) -> None:
        _deprecated("YaplotDocument.RandomPalettes()", "フレームの palettes(random_colors(...))")
        self._legacy_frame().RandomPalettes(N, offset, _quiet=True)

    def RainbowPalettes(self, N: int, offset: int = 10) -> None:
        _deprecated("YaplotDocument.RainbowPalettes()", "フレームの palettes(rainbow_colors(...))")
        self._legacy_frame().RainbowPalettes(N, offset, _quiet=True)

    def Points(
        self,
        points: Iterable[Sequence[float]],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
    ) -> None:
        _deprecated("YaplotDocument.Points()", "フレームの add_many('circle', points)")
        self._legacy_frame().Points(points, layer, color, size, _quiet=True)

    def LinesBatch(
        self,
        segments: Iterable[tuple[Sequence[float], Sequence[float]]],
        layer: int = -1,
        color: int = -1,
    ) -> None:
        _deprecated("YaplotDocument.LinesBatch()", "フレームの add_many('line', coords)")
        self._legacy_frame().LinesBatch(segments, layer, color, _quiet=True)

    def ArrowsBatch(
        self,
        segments: Iterable[tuple[Sequence[float], Sequence[float]]],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        arrowtype: int = -1,
    ) -> None:
        _deprecated("YaplotDocument.ArrowsBatch()", "フレームの add_many('stick', coords)")
        self._legacy_frame().ArrowsBatch(segments, layer, color, size, arrowtype, _quiet=True)
