"""Yaplot 描画コマンドの種類表。

描画コマンドはどれも「種類・座標の列・（あれば）文字列」という同じ形をしている。
種類ごとの違いはこの表だけに書き、仕様にコマンドが増えたら行を足す。
"""

from dataclasses import dataclass
from typing import Literal, Optional


Kind = Literal[
    "line",
    "polyline",
    "stick",
    "polygon",
    "circle",
    "ring",
    "triangle",
    "square",
    "pentagon",
    "hexagon",
    "text",
]


@dataclass(frozen=True, slots=True)
class KindSpec:
    """1 種類の描画コマンドの書式。

    command:
        出力するコマンド文字。Yaplot がまだ受け付けない種類は None。
    npoints:
        1 要素あたりの座標の数。頂点数が可変のときは None。
    min_points:
        npoints が None のときの最小頂点数。
    has_text:
        文字列を伴うか。
    lower_to:
        出力時に分解する先の種類。分解先は座標 2 個の種類に限る
        （折れ線なら隣り合う頂点を結ぶ線分になる）。
        command が付いたあとも、dumps(lower=True) ではこちらに分解する。
    """

    command: Optional[str]
    npoints: Optional[int]
    min_points: int = 1
    has_text: bool = False
    lower_to: Optional[str] = None


KINDS: dict[str, KindSpec] = {
    "line": KindSpec("l", npoints=2),
    # Yaplot 本体はまだ polyline を受け付けない。書き出し時に line へ分解する。
    # 対応したら command をコマンド文字に変えるだけで、そのまま出力できる。
    "polyline": KindSpec(None, npoints=None, min_points=2, lower_to="line"),
    "stick": KindSpec("s", npoints=2),
    "polygon": KindSpec("p", npoints=None, min_points=3),
    "circle": KindSpec("c", npoints=1),
    "ring": KindSpec("o", npoints=1),
    "triangle": KindSpec("3", npoints=1),
    "square": KindSpec("4", npoints=1),
    "pentagon": KindSpec("5", npoints=1),
    "hexagon": KindSpec("6", npoints=1),
    "text": KindSpec("t", npoints=1, has_text=True),
}


def _check_table() -> None:
    for name, spec in KINDS.items():
        if spec.npoints is not None and spec.npoints < 1:
            raise RuntimeError(f"{name}: npoints が不正です")
        if spec.lower_to is None:
            continue
        target = KINDS.get(spec.lower_to)
        if target is None:
            raise RuntimeError(f"{name}: lower_to={spec.lower_to!r} が種類表にありません")
        if target.npoints != 2:
            raise RuntimeError(f"{name}: lower_to は座標 2 個の種類に限る")


_check_table()
