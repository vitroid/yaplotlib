"""非推奨の関数と CamelCase メソッド。"""

import warnings

import pytest

from yaplotlib import (
    Arrow,
    Circle,
    Color,
    Line,
    NewPage,
    RandomPalettes,
    SetPalette,
    Size,
    Text,
    Yaplot,
    YaplotDocument,
    random_colors,
)
from yaplotlib.palettes import gradation_colors


def test_module_functions_warn_and_keep_their_text() -> None:
    with pytest.warns(DeprecationWarning):
        assert Line((0, 0, 0), (1, 0, 0)) == (
            "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        )
    with pytest.warns(DeprecationWarning):
        assert Text((0, 0, 0), "hi") == "t 0.0000 0.0000 0.0000  hi\n"
    with pytest.warns(DeprecationWarning):
        assert Circle((0, 0, 0)) == "c 0.0000 0.0000 0.0000 \n"
    with pytest.warns(DeprecationWarning):
        assert Arrow((0, 0, 0), (1, 0, 0)) == (
            "s 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        )
    with pytest.warns(DeprecationWarning):
        assert Color(3) == "@ 3\n"
    with pytest.warns(DeprecationWarning):
        assert Size(1.5) == "r 1.5\n"
    with pytest.warns(DeprecationWarning):
        assert SetPalette(4, 10, 20, 30) == "@ 4 10 20 30\n"
    with pytest.warns(DeprecationWarning):
        assert SetPalette(4, (255, 128, 0), maxval=255) == "@ 4 255 128 0\n"
    with pytest.warns(DeprecationWarning):
        assert NewPage() == "\n"


def test_string_palette_helpers_do_not_warn() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        text = RandomPalettes(1, offset=10)
    assert random_colors(1) == [(255, 127, 127)]
    assert text == "@ 10 255 127 127\n"
    assert gradation_colors(3, (0, 0, 0), (255, 255, 255))[1] == (127, 127, 127)


def test_new_api_does_not_warn() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        doc = YaplotDocument()
        frame = doc.new_frame()
        frame.add("line", (0, 0, 0), (1, 0, 0), color=3)
        frame.add_many("circle", [[0, 0, 0], [1, 0, 0]])
        frame.palette(4, (1, 2, 3))
        assert "l " in doc.dumps()


def test_camel_case_warns_once_and_draws() -> None:
    drawing = Yaplot()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        drawing.Color(3)
        drawing.Line((0, 0, 0), (1, 0, 0))
        drawing.Circle((0, 0, 0), size=0.5)
    deprecated = [item for item in caught if issubclass(item.category, DeprecationWarning)]
    assert len(deprecated) == 3
    assert drawing.dumps() == (
        "@ 3\n"
        "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        "r 0.5\n"
        "c 0.0000 0.0000 0.0000 \n"
    )


def test_arrow_type_one_is_written() -> None:
    drawing = Yaplot()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        drawing.ArrowType(1)
        drawing.Arrow((0, 0, 0), (1, 0, 0))
    assert drawing.dumps() == (
        "a 1\n"
        "s 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
    )


def test_set_palette_selects_that_color() -> None:
    drawing = Yaplot()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        drawing.SetPalette(5, 255, 0, 0)
        drawing.Line((0, 0, 0), (1, 0, 0))
    assert drawing.dumps() == (
        "@ 5 255 0 0\n"
        "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
    )

    drawing = Yaplot()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        drawing.SetPalette(5, 255, 0, 0)
        drawing.Color(2)
        drawing.Line((0, 0, 0), (1, 0, 0))
    assert drawing.dumps() == (
        "@ 5 255 0 0\n"
        "@ 2\n"
        "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
    )


def test_document_legacy_creates_a_frame_and_warns_once() -> None:
    doc = YaplotDocument()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        doc.Circle((0, 0, 0))
    deprecated = [item for item in caught if issubclass(item.category, DeprecationWarning)]
    assert len(deprecated) == 1
    assert len(doc) == 1
    assert doc.dumps() == "c 0.0000 0.0000 0.0000 \n"


def test_new_page_resets_color() -> None:
    drawing = Yaplot()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        drawing.Color(4)
        drawing.Line((0, 0, 0), (1, 0, 0))
        drawing.NewPage()
        drawing.Line((0, 0, 0), (0, 1, 0))
    assert drawing.dumps() == (
        "@ 4\n"
        "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
        "\n"
        "l 0.0000 0.0000 0.0000 0.0000 1.0000 0.0000 \n"
    )


def test_default_line_has_no_color_command() -> None:
    drawing = Yaplot()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        drawing.Line((0, 0, 0), (1, 0, 0))
        drawing.Layer(1)
        drawing.Size(1)
    assert drawing.dumps() == "l 0.0000 0.0000 0.0000 1.0000 0.0000 0.0000 \n"
