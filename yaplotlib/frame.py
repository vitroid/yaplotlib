"""Frame-level high-level API for Yaplot."""

from typing import Iterable, Sequence, Tuple, Optional, Union

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


class YaplotFrame:
    """Yaplot の 1 フレーム分のコマンド列を蓄積するクラス。"""

    def __init__(self) -> None:
        self.s: str = ""
        self.layer: int = 1
        self.color: int = 2
        self.size: float = 1.0
        self.arrowtype: int = 1

    def Layer(self, layer: int) -> None:
        """現在のレイヤーを変更する。負値の場合は何もしない。"""
        if layer < 0:
            return
        if layer != self.layer:
            self.s += Layer(layer)
            self.layer = layer

    def Color(self, color: int) -> None:
        """現在の色番号を変更する。負値の場合は何もしない。"""
        if color < 0:
            return
        if color != self.color:
            self.s += Color(color)
            self.color = color

    def Size(self, size: float) -> None:
        """現在のサイズ（太さ）を変更する。負値の場合は何もしない。"""
        if size < 0:
            return
        if size != self.size:
            self.s += Size(size)
            self.size = size

    def ArrowType(self, arrowtype: int) -> None:
        """現在の矢印スタイルを変更する。負値の場合は何もしない。"""
        if arrowtype < 0:
            return
        if arrowtype != self.arrowtype:
            self.s += ArrowType(arrowtype)
            self.arrowtype = arrowtype

    def Line(
        self,
        a: Sequence[float],
        b: Sequence[float],
        layer: int = -1,
        color: int = -1,
    ) -> None:
        """線分 a-b を描画する。レイヤー・色を指定すればその都度切り替える。"""
        if layer >= 0:
            self.Layer(layer)
        if color >= 0:
            self.Color(color)
        self.s += Line(a, b)

    def Arrow(
        self,
        a: Sequence[float],
        b: Sequence[float],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        arrowtype: int = -1,
    ) -> None:
        """矢印 a→b を描画する。レイヤー・色・サイズ・矢印タイプを必要に応じて切り替える。"""
        if layer >= 0:
            self.Layer(layer)
        if color >= 0:
            self.Color(color)
        if size >= 0:
            self.Size(size)
        if arrowtype >= 0:
            self.ArrowType(arrowtype)
        self.s += Arrow(a, b)

    def Polygon(
        self,
        p: Iterable[Sequence[float]],
        layer: int = -1,
        color: int = -1,
    ) -> None:
        """頂点列 p で囲まれた多角形を描画する。"""
        if layer >= 0:
            self.Layer(layer)
        if color >= 0:
            self.Color(color)
        self.s += Polygon(p)

    def Circle(
        self,
        c: Sequence[float],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
    ) -> None:
        """中心 c に円（点）を描画する。"""
        if layer >= 0:
            self.Layer(layer)
        if color >= 0:
            self.Color(color)
        if size >= 0:
            self.Size(size)
        self.s += Circle(c)

    def SetPalette(
        self,
        x: int,
        R: Union[int, Sequence[float]],
        G: Optional[float] = None,
        B: Optional[float] = None,
        maxval: float = 255.0,
    ) -> None:
        """パレット x の RGB を設定するコマンドを追加する。"""
        self.s += SetPalette(x, R, G, B, maxval)

    def GradationPalettes(
        self,
        N: int,
        color: Sequence[float],
        color1: Sequence[float],
        offset: int = 10,
        maxval: float = 255.0,
    ) -> None:
        """グラデーションパレットをまとめて追加する。"""
        self.s += GradationPalettes(N, color, color1, offset, maxval)

    def RandomPalettes(self, N: int, offset: int = 10) -> None:
        """ランダムパレットを追加する。"""
        self.s += RandomPalettes(N, offset)

    def RainbowPalettes(self, N: int, offset: int = 10) -> None:
        """虹色パレットを追加する。"""
        self.s += RainbowPalettes(N, offset)

    def NewPage(self) -> None:
        """同一フレーム内でページ区切りを挿入し、状態をリセットする。"""
        self.s += NewPage()
        self.layer = 1
        self.color = 2
        self.arrowtype = 1
        self.size = 1.0

    def dumps(self) -> str:
        """現在までに蓄積された Yaplot コマンド文字列を返す。"""
        return self.s

    # 高レベルユーティリティメソッド
    def save(self, path: str) -> None:
        """このフレームの内容だけをファイルに書き出す。"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.s)

    def Points(
        self,
        points: Iterable[Sequence[float]],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
    ) -> None:
        """点群をまとめて描画するヘルパー。"""
        for p in points:
            self.Circle(p, layer=layer, color=color, size=size)

    def LinesBatch(
        self,
        segments: Iterable[Tuple[Sequence[float], Sequence[float]]],
        layer: int = -1,
        color: int = -1,
    ) -> None:
        """線分群をまとめて描画するヘルパー。"""
        for a, b in segments:
            self.Line(a, b, layer=layer, color=color)

    def ArrowsBatch(
        self,
        segments: Iterable[Tuple[Sequence[float], Sequence[float]]],
        layer: int = -1,
        color: int = -1,
        size: float = -1,
        arrowtype: int = -1,
    ) -> None:
        """矢印群をまとめて描画するヘルパー。"""
        for a, b in segments:
            self.Arrow(a, b, layer=layer, color=color, size=size, arrowtype=arrowtype)


# 互換用エイリアス（1フレーム = 従来の Yaplot）
Yaplot = YaplotFrame
