import pytest

from photonx_eda_pcb.kicad_reader import read_kicad_board_text


@pytest.mark.parametrize(
    "text",
    [
        '(kicad_pcb (net 1.5 "SIG"))',
        (
            '(kicad_pcb (net 1 "SIG") '
            '(segment (start 0 0) (end 1 0) (width 0.2) '
            '(layer "F.Cu") (net 1.5)))'
        ),
        (
            '(kicad_pcb (net 1 "SIG") '
            '(via (at 0 0) (size 1) (drill 0.5) '
            '(layers "F.Cu" "B.Cu") (net 1.5)))'
        ),
        (
            '(kicad_pcb (net 1 "SIG") '
            '(footprint "X" (layer "F.Cu") '
            '(pad "1" smd rect (at 0 0) (size 1 1) '
            '(layers "F.Cu") (net 1.5 "SIG"))))'
        ),
    ],
)
def test_reader_rejects_fractional_net_ordinals(text):
    with pytest.raises(ValueError, match="must be an integer"):
        read_kicad_board_text(text)


def test_reader_rejects_duplicate_net_ordinals():
    with pytest.raises(ValueError, match="duplicate net ordinal 1"):
        read_kicad_board_text(
            '(kicad_pcb (net 1 "GND") (net 1 "VCC"))'
        )


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        (
            '(kicad_pcb (net 1 "SIG") '
            '(segment (start 0 0) (end 1 0) (width 0.2) '
            '(layer "F.Cu") (net 2)))',
            "segment",
        ),
        (
            '(kicad_pcb (net 1 "SIG") '
            '(via (at 0 0) (size 1) (drill 0.5) '
            '(layers "F.Cu" "B.Cu") (net 2)))',
            "via",
        ),
        (
            '(kicad_pcb (net 1 "SIG") '
            '(footprint "X" (layer "F.Cu") '
            '(pad "1" smd rect (at 0 0) (size 1 1) '
            '(layers "F.Cu") (net 2 "OTHER"))))',
            "pad",
        ),
    ],
)
def test_reader_rejects_dangling_net_references(text, kind):
    with pytest.raises(
        ValueError, match=rf"{kind} references undefined net ordinal 2"
    ):
        read_kicad_board_text(text)


def test_reader_preserves_valid_integer_net_references():
    board = read_kicad_board_text(
        '(kicad_pcb (net 1 "SIG") '
        '(segment (start 0 0) (end 1 0) (width 0.2) '
        '(layer "F.Cu") (net 1)) '
        '(via (at 0 0) (size 1) (drill 0.5) '
        '(layers "F.Cu" "B.Cu") (net 1)) '
        '(footprint "X" (layer "F.Cu") '
        '(pad "1" smd rect (at 0 0) (size 1 1) '
        '(layers "F.Cu") (net 1 "SIG"))))'
    )

    assert board["nets"] == [{"code": 1, "name": "SIG"}]
    assert board["segments"][0]["net"] == 1
    assert board["vias"][0]["net"] == 1
    assert board["footprints"][0]["pads"][0]["net"] == 1
