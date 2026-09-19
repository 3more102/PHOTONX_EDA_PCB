import math

import pytest

from photonx_eda_pcb.kicad_reader.sexpr import parse_sexpr


@pytest.mark.parametrize(
    "atom",
    [
        "nan",
        "NaN",
        "inf",
        "+inf",
        "-inf",
        "Infinity",
        "-Infinity",
        "1e309",
        "-1e309",
    ],
)
def test_non_finite_numeric_atoms_are_rejected(atom: str):
    with pytest.raises(ValueError, match="non-finite numeric atom"):
        parse_sexpr(f"(value {atom})")


def test_finite_scientific_notation_remains_supported():
    result = parse_sexpr("(value 1.25e3)")

    assert result == ["value", 1250.0]
    assert math.isfinite(result[1])


def test_quoted_non_finite_words_remain_plain_strings():
    assert parse_sexpr('(value "nan" "inf")') == ["value", "nan", "inf"]


def test_kicad_geometry_cannot_carry_non_finite_coordinates():
    text = """
    (kicad_pcb
      (segment
        (start 1e309 0)
        (end 1 1)
        (width 0.25)
        (layer "F.Cu")
        (net 1)))
    """

    with pytest.raises(ValueError, match="non-finite numeric atom"):
        parse_sexpr(text)
