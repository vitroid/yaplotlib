"""ファイル全体に共通する global ブロック。"""

from dataclasses import dataclass, field
from typing import Optional, Union

from .elements import Rgb, Svg, coerce_svg


@dataclass(slots=True)
class Globals:
    """以降の全フレームに効く既定値と、全フレーム共通の SVG。

    何も設定していなければ、global ブロック自体を出力しない。
    ここに置いた SVG はすべてのフレームに重ねて表示される。
    ``center`` を真にすると、引数のない ``center`` を出し、最初のフレームで中央表示にする。
    """

    layer: Optional[int] = None
    color: Optional[int] = None
    radius: Optional[float] = None
    arrow: Optional[int] = None
    palettes: dict[int, Rgb] = field(default_factory=dict)
    reality: Optional[int] = None
    splat: Optional[int] = None
    fov: Optional[float] = None
    verbose: Optional[int] = None
    thickness: Optional[int] = None
    rotation: Optional[tuple[float, ...]] = None
    fps: Optional[float] = None
    hide: tuple[int, ...] = ()
    show: tuple[int, ...] = ()
    center: bool = False
    messages: list[str] = field(default_factory=list)
    svgs: list[Svg] = field(default_factory=list)

    def add_svg(self, svg: Union[Svg, str, object]) -> Svg:
        """全フレーム共通の SVG を追加する。

        文字列、ファイルパス、matplotlib の Figure、:class:`Svg` を受け付ける。
        """
        svg = coerce_svg(svg)
        self.svgs.append(svg)
        return svg

    def is_empty(self) -> bool:
        """出力すべき設定が一つも無いか。"""
        return (
            self.layer is None
            and self.color is None
            and self.radius is None
            and self.arrow is None
            and not self.palettes
            and self.reality is None
            and self.splat is None
            and self.fov is None
            and self.verbose is None
            and self.thickness is None
            and self.rotation is None
            and self.fps is None
            and not self.hide
            and not self.show
            and not self.center
            and not self.messages
            and not self.svgs
        )
