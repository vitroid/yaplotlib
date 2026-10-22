"""要素の列を Yaplot のテキストに変換する。

状態（レイヤ・色・半径・矢印）の差分はここでだけ計算する。
フレームは状態を持たない。
"""

import operator
from typing import Optional, Sequence, Union

import numpy as np

from .elements import (
    Batch,
    FrameBreak,
    PaletteDef,
    Primitive,
    Svg,
    _as_int,
    _as_radius,
)
from .globals import Globals
from .spec import KINDS

# Yaplot 本体の初期値。色だけは線が 0、塗りが 2 と分かれているため未確定にする。
_DEFAULT_LAYER = 1
_DEFAULT_RADIUS = 1.0
_DEFAULT_ARROW = 0


def quote_text(text: str) -> str:
    """空白や引用符を含む文字列を Yaplot の ``"..."`` にする。"""
    if "\n" in text or "\r" in text:
        raise ValueError("改行を含む文字列は出力できません")
    if text == "" or any(char.isspace() or char in '"\\' for char in text):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def format_command(
    command: str,
    points: Sequence[Sequence[float]],
    *,
    count: bool = False,
    text: Optional[str] = None,
) -> str:
    """描画コマンド 1 行を作る。座標の末尾には従来どおり空白を付ける。"""
    parts = [command]
    if count:
        parts.append(str(len(points)))
    for point in points:
        for coord in point:
            parts.append(f"{float(coord):.4f}")
    line = " ".join(parts) + " "
    if text is not None:
        line += " " + quote_text(text)
    return line + "\n"


def format_palette(index: int, rgb: Sequence[int]) -> str:
    """``@ n r g b`` の 1 行を作る。"""
    red, green, blue = rgb
    return f"@ {int(index)} {int(red)} {int(green)} {int(blue)}\n"


class _State:
    """書き出し中の、Yaplot 側の現在の状態。"""

    def __init__(self, defaults: Optional[Globals]) -> None:
        self.layer = _DEFAULT_LAYER
        self.radius = _DEFAULT_RADIUS
        self.arrow = _DEFAULT_ARROW
        self.color: Optional[int] = None
        if defaults is not None:
            if defaults.layer is not None:
                self.layer = _as_int("layer", defaults.layer, 1)
            if defaults.radius is not None:
                self.radius = _as_radius(defaults.radius)
            if defaults.arrow is not None:
                self.arrow = _as_int("arrow", defaults.arrow, 0)
            self.color = _opening_color(defaults)
        self._initial = (self.layer, self.radius, self.arrow, self.color)

    def reset(self) -> None:
        self.layer, self.radius, self.arrow, self.color = self._initial


def _opening_color(defaults: Globals) -> Optional[int]:
    """global ブロックを読み終えた時点で選ばれている色。"""
    if defaults.color is not None:
        return _as_int("color", defaults.color, 0)
    if not defaults.palettes:
        return None
    last = sorted(defaults.palettes)[-1]
    return _as_int("palette", last, 0)


def _lowering(kind: str, lower: bool) -> bool:
    spec = KINDS[kind]
    if lower and spec.lower_to:
        return True
    if spec.command is None:
        raise ValueError(
            f"{kind!r} にはまだ Yaplot のコマンドがありません。"
            " dumps(lower=True) で線分に分解して出力できます。"
        )
    return False


def _emit_style(state: _State, item: Union[Primitive, Batch], out: list[str]) -> None:
    if item.layer is not None and item.layer != state.layer:
        state.layer = item.layer
        out.append(f"y {state.layer}\n")
    if item.color is not None and item.color != state.color:
        state.color = item.color
        out.append(f"@ {state.color}\n")
    if item.radius is not None and item.radius != state.radius:
        state.radius = item.radius
        out.append(f"r {state.radius}\n")
    if item.arrow is not None and item.arrow != state.arrow:
        state.arrow = item.arrow
        out.append(f"a {state.arrow}\n")


def _emit_primitive(state: _State, prim: Primitive, out: list[str], lower: bool) -> None:
    spec = KINDS[prim.kind]
    _emit_style(state, prim, out)
    if _lowering(prim.kind, lower):
        command = KINDS[spec.lower_to].command  # type: ignore[index]
        points = prim.points
        for start, end in zip(points, points[1:]):
            out.append(format_command(command or "", (start, end)))
        return
    out.append(
        format_command(
            spec.command or "",
            prim.points,
            count=spec.npoints is None,
            text=prim.text,
        )
    )


def _emit_batch(state: _State, batch: Batch, out: list[str], lower: bool) -> None:
    spec = KINDS[batch.kind]
    lowering = _lowering(batch.kind, lower)
    _emit_style(state, batch, out)
    if lowering:
        command = KINDS[spec.lower_to].command or ""  # type: ignore[union-attr]
        if isinstance(batch.coords, np.ndarray):
            out.append(_format_block(command, _chains_to_lines(batch.coords), None, False))
        else:
            for array in batch.coords:
                for index in range(array.shape[0] - 1):
                    out.append(format_command(command, (array[index], array[index + 1])))
        return
    if isinstance(batch.coords, np.ndarray):
        out.append(
            _format_block(spec.command or "", batch.coords, batch.texts, spec.npoints is None)
        )
        return
    for index, array in enumerate(batch.coords):
        text = None if batch.texts is None else batch.texts[index]
        out.append(format_command(spec.command or "", array, count=True, text=text))


def _emit_palette(state: _State, item: PaletteDef, out: list[str]) -> None:
    out.append(format_palette(item.index, item.rgb))
    # @ n r g b はパレット n を現在の色としても選ぶ。
    state.color = item.index


def _chains_to_lines(coords: np.ndarray) -> np.ndarray:
    """(N, m, 3) の折れ線を、隣り合う頂点を結ぶ (N*(m-1), 2, 3) の線分にする。"""
    if coords.shape[0] == 0 or coords.shape[1] < 2:
        return np.zeros((0, 2, 3), dtype=float)
    paired = np.stack((coords[:, :-1, :], coords[:, 1:, :]), axis=2)
    return paired.reshape(-1, 2, 3)


def _format_block(
    command: str,
    coords: np.ndarray,
    texts: Optional[tuple[str, ...]],
    with_count: bool,
) -> str:
    """(N, k, 3) をコマンドの行にまとめて整形する。"""
    count = int(coords.shape[0])
    if count == 0:
        return ""
    width = int(coords.shape[1])
    formatted = np.char.mod("%.4f", coords.reshape(count, width * 3))
    prefix = f"{command} {width} " if with_count else f"{command} "
    lines: list[str] = []
    for index in range(count):
        line = prefix + " ".join(formatted[index].tolist()) + " "
        if texts is not None:
            line += " " + quote_text(texts[index])
        lines.append(line + "\n")
    return "".join(lines)


def _svg_text(svg: Svg) -> str:
    text = svg.text
    if not text.endswith("\n"):
        return text + "\n"
    return text


def render_frame(
    items: Sequence[object],
    svgs: Sequence[Svg],
    defaults: Optional[Globals],
    lower: bool = True,
) -> str:
    """1 フレーム分をテキストにする。末尾にフレーム区切りの空行は付けない。"""
    state = _State(defaults)
    out: list[str] = []
    for item in items:
        if isinstance(item, FrameBreak):
            out.append("\n")
            state.reset()
            continue
        if isinstance(item, PaletteDef):
            _emit_palette(state, item, out)
        elif isinstance(item, Batch):
            _emit_batch(state, item, out, lower)
        elif isinstance(item, Primitive):
            _emit_primitive(state, item, out, lower)
        else:
            raise TypeError(f"フレームに置けない要素です: {type(item).__name__}")
    for svg in svgs:
        out.append(_svg_text(svg))
    return "".join(out)


def _join_frames(texts: Sequence[str]) -> str:
    out: list[str] = []
    last = len(texts) - 1
    for index, text in enumerate(texts):
        if text and not text.endswith("\n"):
            text += "\n"
        out.append(text)
        if index != last:
            out.append("\n")
    return "".join(out)


def render_document(defaults: Globals, frames: Sequence[object], lower: bool = True) -> str:
    """global ブロックと全フレームを 1 つのテキストにする。"""
    parts: list[str] = []
    if not defaults.is_empty():
        parts.append(render_globals(defaults))
    rendered = [
        render_frame(frame.items, frame.svgs, defaults, lower)  # type: ignore[attr-defined]
        for frame in frames
    ]
    parts.append(_join_frames(rendered))
    return "".join(parts)


def render_globals(defaults: Globals) -> str:
    """global ブロックを、終端の空行まで含めて作る。"""
    lines = ["global\n"]
    if defaults.reality is not None:
        lines.append(f"reality {_int_between('reality', defaults.reality, 0, 4)}\n")
    if defaults.splat is not None:
        lines.append(f"splat {_int_between('splat', defaults.splat, 0, 3)}\n")
    if defaults.fov is not None:
        lines.append(f"fov {_float_token(_as_float('fov', defaults.fov))}\n")
    if defaults.verbose is not None:
        lines.append(f"verbose {_int_between('verbose', defaults.verbose, 0, 3)}\n")
    if defaults.thickness is not None:
        lines.append(f"thickness {_plain_int('thickness', defaults.thickness)}\n")
    if defaults.rotation is not None:
        lines.append("rotation " + _rotation(defaults.rotation) + "\n")
    if defaults.fps is not None:
        lines.append(f"fps {_float_token(_as_float('fps', defaults.fps))}\n")
    if defaults.hide:
        lines.append("hide " + _layers("hide", defaults.hide) + "\n")
    if defaults.show:
        lines.append("show " + _layers("show", defaults.show) + "\n")
    for message in defaults.messages:
        if not isinstance(message, str):
            raise TypeError("message は文字列にしてください")
        lines.append("message " + quote_text(message) + "\n")
    if defaults.radius is not None:
        lines.append(f"r {_as_radius(defaults.radius)}\n")
    if defaults.layer is not None:
        lines.append(f"y {_as_int('layer', defaults.layer, 1)}\n")
    if defaults.arrow is not None:
        lines.append(f"a {_as_int('arrow', defaults.arrow, 0)}\n")
    for index in sorted(defaults.palettes):
        item = PaletteDef(index, defaults.palettes[index])
        lines.append(format_palette(item.index, item.rgb))
    if defaults.color is not None:
        color = _as_int("color", defaults.color, 0)
        last: Optional[int] = None
        if defaults.palettes:
            last = _as_int("palette", sorted(defaults.palettes)[-1], 0)
        # 直前の @ n r g b がすでにこの色を選んでいれば、繰り返し出力しない。
        if last != color:
            lines.append(f"@ {color}\n")
    for svg in defaults.svgs:
        lines.append(_svg_text(svg))
    lines.append("\n")
    return "".join(lines)


def _plain_int(name: str, value: object) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} は整数で指定してください")
    try:
        return operator.index(value)  # type: ignore[arg-type]
    except TypeError:
        raise TypeError(f"{name} は整数で指定してください") from None


def _int_between(name: str, value: object, lo: int, hi: int) -> int:
    number = _plain_int(name, value)
    if not lo <= number <= hi:
        raise ValueError(f"{name} は {lo}..{hi} の範囲です: {number}")
    return number


def _as_float(name: str, value: object) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} は数値で指定してください")
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise TypeError(f"{name} は数値で指定してください") from None


def _float_token(value: float) -> str:
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return format(value, ".6g")


def _rotation(value: object) -> str:
    try:
        numbers = tuple(_as_float("rotation", item) for item in value)  # type: ignore[union-attr]
    except TypeError:
        raise TypeError("rotation は 1〜3 個の数値にしてください") from None
    if not 1 <= len(numbers) <= 3:
        raise ValueError(f"rotation は 1〜3 個の数値にしてください（{len(numbers)} 個渡されました）")
    return " ".join(_float_token(number) for number in numbers)


def _layers(name: str, values: object) -> str:
    try:
        numbers = [_as_int(name, item, 1) for item in values]  # type: ignore[union-attr]
    except TypeError:
        raise TypeError(f"{name} はレイヤ番号の列にしてください") from None
    return " ".join(str(number) for number in numbers)
