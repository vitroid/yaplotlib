"""Multi-frame document API for Yaplot."""

from typing import Iterable, Sequence, Tuple

from .frame import YaplotFrame


class YaplotDocument:
    """複数フレームからなる Yaplot ドキュメントを表すクラス。"""

    def __init__(self) -> None:
        self.frames: list[YaplotFrame] = [YaplotFrame()]
        self.current_index: int = 0

    @property
    def current(self) -> YaplotFrame:
        """現在アクティブなフレームを返す。"""
        return self.frames[self.current_index]

    def new_frame(self) -> YaplotFrame:
        """新しいフレームを追加して、それをアクティブにする。"""
        frame = YaplotFrame()
        self.frames.append(frame)
        self.current_index = len(self.frames) - 1
        return frame

    # 代表的な描画メソッドは現在フレームへ委譲する
    def Layer(self, *args, **kwargs) -> None:
        self.current.Layer(*args, **kwargs)

    def Color(self, *args, **kwargs) -> None:
        self.current.Color(*args, **kwargs)

    def Size(self, *args, **kwargs) -> None:
        self.current.Size(*args, **kwargs)

    def ArrowType(self, *args, **kwargs) -> None:
        self.current.ArrowType(*args, **kwargs)

    def Line(self, *args, **kwargs) -> None:
        self.current.Line(*args, **kwargs)

    def Arrow(self, *args, **kwargs) -> None:
        self.current.Arrow(*args, **kwargs)

    def Polygon(self, *args, **kwargs) -> None:
        self.current.Polygon(*args, **kwargs)

    def Circle(self, *args, **kwargs) -> None:
        self.current.Circle(*args, **kwargs)

    def SetPalette(self, *args, **kwargs) -> None:
        self.current.SetPalette(*args, **kwargs)

    def GradationPalettes(self, *args, **kwargs) -> None:
        self.current.GradationPalettes(*args, **kwargs)

    def RandomPalettes(self, *args, **kwargs) -> None:
        self.current.RandomPalettes(*args, **kwargs)

    def RainbowPalettes(self, *args, **kwargs) -> None:
        self.current.RainbowPalettes(*args, **kwargs)

    def Points(self, *args, **kwargs) -> None:
        self.current.Points(*args, **kwargs)

    def LinesBatch(self, *args, **kwargs) -> None:
        self.current.LinesBatch(*args, **kwargs)

    def ArrowsBatch(self, *args, **kwargs) -> None:
        self.current.ArrowsBatch(*args, **kwargs)

    def dumps(self) -> str:
        """全フレームを連結した Yaplot コマンド文字列を返す。"""
        # フレーム間に空行を挟んでページ区切りとする
        return "\n\n".join(frame.dumps().rstrip("\n") for frame in self.frames)

    def save(self, path: str) -> None:
        """全フレームを含むドキュメントをファイルに書き出す。"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.dumps())
