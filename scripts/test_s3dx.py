"""Tests for the formatting-preserving Shape3d .s3dx reader/writer."""
from pathlib import Path

import pytest

import s3dx

BOARD = Path(__file__).parent.parent / "projects/Surfboards/7-6-22_7_8-3-Kustom-Beak.s3dx"


@pytest.fixture(scope="module")
def original_bytes():
    return BOARD.read_bytes()


@pytest.fixture()
def doc():
    return s3dx.load(BOARD)


def test_roundtrip_is_byte_identical(doc, original_bytes):
    assert doc.tobytes() == original_bytes


def test_tree_navigation(doc):
    board = doc.root.find("Board")
    assert board.find("Name").text == "Kustom"
    assert board.find("Author").text == "Brian"
    assert len(board.findall("Couples_*")) == 8
    # the malformed tag with a space is a navigable element
    ref = board.find("Box_0").find("Box").find("Ref. point")
    assert ref.find("Point3d").find("x").text == "15.160004"
    # raw ampersand in License survives untouched
    assert "&" in board.find("License").text
    # empty element reads as empty string
    assert board.find("Comment").text == ""


def outline_anchors(doc):
    poly = doc.root.find("Board").find("Otl").find("Bezier3d").find("Control_points").find("Polygone3d")
    # direct children only: the Symmetry_center's Point3d is nested one level down
    return poly.findall("Point3d")


def test_set_text_rewrites_exactly_that_element(doc, original_bytes):
    doc.root.find("Board").find("Name").set_text("Kustom Claude")
    expected = original_bytes.replace(b"<Name>Kustom</Name>", b"<Name>Kustom Claude</Name>")
    assert expected != original_bytes
    assert doc.tobytes() == expected


def test_set_text_refuses_non_leaf(doc):
    with pytest.raises(ValueError):
        doc.root.find("Board").find("Otl").set_text("boom")


def test_float_read_and_write(doc, original_bytes):
    anchors = outline_anchors(doc)
    assert len(anchors) == 3
    wide = anchors[1]
    assert wide.find("y").float == pytest.approx(29.051250)
    wide.find("y").set_float(29.5)
    assert wide.find("y").text == "29.500000"
    # the outline lives twice in the file (Otl and its OutlineDef copy);
    # our edit touches only Otl, so replace only the first occurrence here
    pair = b"<x>121.239482</x><y>29.051250</y>"
    assert original_bytes.count(pair) == 2
    expected = original_bytes.replace(pair, b"<x>121.239482</x><y>29.500000</y>", 1)
    assert doc.tobytes() == expected


def test_save_roundtrip(doc, original_bytes, tmp_path):
    out = tmp_path / "copy.s3dx"
    doc.save(out)
    assert out.read_bytes() == original_bytes
