"""書き出し。global、状態差分、polyline、Batch。"""

import numpy as np
import pytest

from yaplotlib import Batch, YaplotDocument, YaplotFrame


def test_empty_document_has_no_global() -> None:
    doc = YaplotDocument()
    assert doc.dumps() == ""
    frame = doc.new_frame()
    frame.add("circle", (0, 0, 0))
    assert "global" not in doc.dumps()
    assert doc.dumps() == "c 0.0000 0.0000 0.0000 \n"
    with pytest.raises(IndexError):
        YaplotDocument().current


def test_global_defaults_apply_to_every_frame() -> None:
    doc = YaplotDocument()
    doc.globals.palettes[3] = (255, 100, 100)
    doc.globals.radius = 0.3
    doc.globals.layer = 1
    doc.globals.arrow = 1
    frame = doc.new_frame()
    frame.add("stick", (0, 0, 0), (1, 0, 0))
    frame.add("circle", (0, 0, 0))
    frame = doc.new_frame()
    frame.add("stick", (0, 0, 0), (0, 1, 0))
    frame.add("circle", (0.5, 0, 0))
    frame = doc.new_frame()
    frame.add("stick", (0, 0, 0), (0, 0, 1))
    assert doc.dumps() == (
        "global\n"
        "r 0.3\n"
        "y 1\n"
        "a 1\n"
        "@ 3 255 100 100\n"
        "\n"
        "s 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        "c 0.0000 0.0000 0.0000 \n"
        "\n"
        "s 0.0000 0.0000 0.0000 0.0000 1.0000 0.0000 \n"
        "c 0.5000 0.0000 0.0000 \n"
        "\n"
        "s 0.0000 0.0000 0.0000 0.0000 0.0000 1.0000 \n"
    )


def test_ui_settings_and_message() -> None:
    doc = YaplotDocument()
    g = doc.globals
    g.reality = 3
    g.splat = 1
    g.fov = 30
    g.verbose = 2
    g.thickness = 4
    g.rotation = (1, 0, 0.5)
    g.fps = 12
    g.hide = (3, 4)
    g.show = (1,)
    g.messages.append("hello world")
    g.messages.append('say "hi"')
    assert doc.dumps() == (
        "global\n"
        "reality 3\n"
        "splat 1\n"
        "fov 30\n"
        "verbose 2\n"
        "thickness 4\n"
        "rotation 1 0 0.5\n"
        "fps 12\n"
        "hide 3 4\n"
        "show 1\n"
        'message "hello world"\n'
        'message "say \\"hi\\""\n'
        "\n"
    )
    doc.globals.reality = 9
    with pytest.raises(ValueError):
        doc.dumps()


def test_style_is_emitted_only_when_it_changes() -> None:
    frame = YaplotFrame()
    frame.add(
        "stick",
        (0, 0, 0),
        (1, 0, 0),
        layer=2,
        color=3,
        radius=0.2,
        arrow=1,
    )
    frame.add("stick", (0, 0, 0), (0, 1, 0), layer=2, color=3, radius=0.2, arrow=1)
    frame.add("circle", (0, 0, 0), color=4, radius=0.5)
    assert frame.dumps() == (
        "y 2\n"
        "@ 3\n"
        "r 0.2\n"
        "a 1\n"
        "s 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        "s 0.0000 0.0000 0.0000 0.0000 1.0000 0.0000 \n"
        "@ 4\n"
        "r 0.5\n"
        "c 0.0000 0.0000 0.0000 \n"
    )


def test_omitted_color_keeps_the_previous_one() -> None:
    frame = YaplotFrame()
    frame.palette(5, (1, 2, 3))
    frame.add("line", (0, 0, 0), (1, 0, 0))
    frame.add("line", (0, 0, 0), (0, 1, 0), color=5)
    frame.add("circle", (0, 0, 0), color=2)
    assert frame.dumps() == (
        "@ 5 1 2 3\n"
        "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        "l 0.0000 0.0000 0.0000 0.0000 1.0000 0.0000 \n"
        "@ 2\n"
        "c 0.0000 0.0000 0.0000 \n"
    )


def test_explicit_global_color_wins_over_the_last_palette() -> None:
    doc = YaplotDocument()
    doc.globals.palettes[4] = (0, 0, 255)
    doc.globals.palettes[3] = (255, 0, 0)
    doc.globals.color = 3
    doc.new_frame().add("line", (0, 0, 0), (1, 0, 0))
    assert doc.dumps() == (
        "global\n"
        "@ 3 255 0 0\n"
        "@ 4 0 0 255\n"
        "@ 3\n"
        "\n"
        "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
    )


def test_text_quoting() -> None:
    frame = YaplotFrame()
    frame.add("text", (0, 0, 0), text="plain")
    frame.add("text", (1, 0, 0), text='say "hi"\\')
    assert frame.dumps() == (
        "t 0.0000 0.0000 0.0000  plain\n"
        't 1.0000 0.0000 0.0000  "say \\"hi\\"\\\\"\n'
    )


def test_polyline_lowers_to_lines() -> None:
    frame = YaplotFrame()
    frame.add("polyline", (0, 0, 0), (1, 0, 0), (1, 1, 0), color=4)
    assert frame.items[0].kind == "polyline"  # type: ignore[union-attr]
    assert frame.dumps() == (
        "@ 4\n"
        "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        "l 1.0000 0.0000 0.0000 1.0000 1.0000 0.0000 \n"
    )
    with pytest.raises(ValueError):
        frame.dumps(lower=False)


def test_batch_matches_separate_primitives() -> None:
    circles = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    many = YaplotFrame()
    batch = many.add_many("circle", circles, color=3)
    assert isinstance(batch, Batch)
    assert len(many.items) == 1
    single = YaplotFrame()
    for point in circles:
        single.add("circle", point, color=3)
    assert many.dumps() == single.dumps()

    segments = np.stack(
        [
            np.array([[0, 0, 0], [1, 0, 0]], dtype=float),
            np.array([[1, 0, 0], [1, 1, 0]], dtype=float),
        ],
        axis=1,
    )
    many = YaplotFrame()
    many.add_many("line", segments, layer=2)
    single = YaplotFrame()
    single.add("line", (0, 0, 0), (1, 0, 0), layer=2)
    single.add("line", (1, 0, 0), (1, 1, 0), layer=2)
    assert many.dumps() == single.dumps()

    polys = [
        np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float),
        np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=float),
    ]
    many = YaplotFrame()
    many.add_many("polygon", polys, color=2)
    single = YaplotFrame()
    single.add("polygon", *polys[0], color=2)
    single.add("polygon", *polys[1], color=2)
    assert many.dumps() == single.dumps()


def test_polyline_batch_lowers_like_separate_polylines() -> None:
    paths = np.zeros((2, 3, 3))
    paths[0] = [[0, 0, 0], [1, 0, 0], [1, 1, 0]]
    paths[1] = [[0, 0, 1], [0, 1, 1], [1, 1, 1]]
    many = YaplotFrame()
    many.add_many("polyline", paths, color=4)
    single = YaplotFrame()
    for path in paths:
        single.add("polyline", *path, color=4)
    assert many.dumps() == single.dumps()
    assert many.dumps().count("l ") == 4


def test_svg_overlay_order() -> None:
    hud = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
        "  <text>title</text>\n"
        "</svg>\n"
    )
    frame_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
        "\n"
        "  <text>t = {t}</text>\n"
        "</svg>\n"
    )
    doc = YaplotDocument()
    doc.globals.reality = 3
    doc.globals.radius = 1
    doc.globals.add_svg(hud)
    for t, z in enumerate((-3, 0)):
        frame = doc.new_frame()
        frame.palette(3, (255, 96, 96))
        frame.add("circle", (-5, 0, z))
        frame.palette(4, (96, 160, 255))
        frame.add("stick", (-5, 0, z), (5, 0, 0))
        frame.add("circle", (5, 0, 0))
        frame.add_svg(frame_svg.format(t=t))

    def body(z: float, t: int) -> str:
        return (
            "@ 3 255 96 96\n"
            f"c -5.0000 0.0000 {z:.4f} \n"
            "@ 4 96 160 255\n"
            f"s -5.0000 0.0000 {z:.4f} 5.0000 0.0000 0.0000 \n"
            "c 5.0000 0.0000 0.0000 \n"
            + frame_svg.format(t=t)
        )

    assert doc.dumps() == (
        "global\n"
        "reality 3\n"
        "r 1.0\n"
        + hud
        + "\n"
        + body(-3, 0)
        + "\n"
        + body(0, 1)
    )


def test_markers_ring_and_polygon_commands() -> None:
    frame = YaplotFrame()
    frame.add("ring", (0, 0, 0))
    frame.add("square", (1, 0, 0))
    frame.add("polygon", (0, 0, 0), (1, 0, 0), (0, 1, 0))
    assert frame.dumps() == (
        "o 0.0000 0.0000 0.0000 \n"
        "4 1.0000 0.0000 0.0000 \n"
        "p 3 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 0.0000 1.0000 0.0000 \n"
    )


def test_save_roundtrip(tmp_path) -> None:
    doc = YaplotDocument()
    doc.new_frame().add("text", (0, 0, 0), text="a b")
    path = tmp_path / "out.yap"
    doc.save(path)
    assert path.read_text(encoding="utf-8") == doc.dumps()


def test_frame_radius_overrides_global() -> None:
    doc = YaplotDocument()
    doc.globals.radius = 0.3
    doc.new_frame().add("circle", (0, 0, 0), radius=0.5)
    text = doc.dumps()
    assert text.startswith("global\nr 0.3\n\n")
    assert text.endswith("r 0.5\nc 0.0000 0.0000 0.0000 \n")
