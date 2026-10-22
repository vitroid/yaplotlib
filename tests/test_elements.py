"""要素の検証と正規化。"""

from pathlib import Path

import numpy as np
import pytest

from yaplotlib import Batch, PaletteDef, Primitive, Svg
from yaplotlib.elements import coerce_svg


def test_primitive_normalizes_numpy_point() -> None:
    prim = Primitive("circle", (np.array([1, 2, 3]),))
    assert prim.points == ((1.0, 2.0, 3.0),)


def test_primitive_rejects_bad_shape_and_kind() -> None:
    with pytest.raises(ValueError):
        Primitive("line", ((0, 0, 0),))
    with pytest.raises(ValueError):
        Primitive("polygon", ((0, 0, 0), (1, 0, 0)))
    with pytest.raises(ValueError):
        Primitive("circle", ((0, 0),))
    with pytest.raises(ValueError):
        Primitive("nope", ((0, 0, 0),))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Primitive("line", ((0, 0, 0), (1, 0, 0)), text="x")
    with pytest.raises(TypeError):
        Primitive("text", ((0, 0, 0),))


def test_batch_shapes() -> None:
    circles = Batch("circle", np.zeros((4, 3)))
    assert isinstance(circles.coords, np.ndarray)
    assert circles.coords.shape == (4, 1, 3)

    lines = Batch("line", np.zeros((4, 2, 3)))
    assert lines.coords.shape == (4, 2, 3)

    with pytest.raises(ValueError):
        Batch("line", np.zeros((2, 3)))
    with pytest.raises(ValueError):
        Batch("polygon", np.zeros((2, 3)))


def test_batch_ragged_polygon_and_text_length() -> None:
    ragged = Batch(
        "polygon",
        [
            np.zeros((3, 3)),
            np.ones((4, 3)),
        ],
    )
    assert isinstance(ragged.coords, tuple)
    assert ragged.coords[0].shape == (3, 3)
    assert ragged.coords[1].shape == (4, 3)

    with pytest.raises(ValueError):
        Batch("text", np.zeros((2, 3)), texts=("only",))
    with pytest.raises(TypeError):
        Batch("circle", np.zeros((1, 3)), texts=("x",))


def test_palette_range() -> None:
    assert PaletteDef(3, (255, 0, 1)).rgb == (255, 0, 1)
    with pytest.raises(ValueError):
        PaletteDef(1, (256, 0, 0))
    with pytest.raises(ValueError):
        PaletteDef(-1, (0, 0, 0))


def test_svg_validation(tmp_path: Path) -> None:
    svg = Svg('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    assert svg.text.startswith("<svg")
    with pytest.raises(ValueError):
        Svg("<svg/>")
    with pytest.raises(ValueError):
        Svg("<!-- note -->")
    with pytest.raises(ValueError):
        Svg("not svg")

    path = tmp_path / "a.svg"
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
    assert Svg.from_file(path).text.startswith("<svg")
    assert coerce_svg(str(path)).text.startswith("<svg")

    class Fig:
        def savefig(self, buf, format, transparent):  # noqa: A002
            assert format == "svg"
            assert transparent is True
            buf.write('<svg xmlns="http://www.w3.org/2000/svg"></svg>')

    assert Svg.from_figure(Fig()).text.startswith("<svg")


def test_polyline_is_stored_as_polyline() -> None:
    prim = Primitive("polyline", ((0, 0, 0), (1, 0, 0), (1, 1, 0)))
    assert prim.kind == "polyline"
    assert len(prim.points) == 3
    with pytest.raises(ValueError):
        Primitive("polyline", ((0, 0, 0),))
