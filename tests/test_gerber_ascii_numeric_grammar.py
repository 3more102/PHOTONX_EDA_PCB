from pathlib import Path

import pytest

from photonx_eda_pcb.aperture_macros import evaluate_macro, parse_macro_body
from photonx_eda_pcb.aperture_macros.variables import substitute
from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.gerber_geometry.macro import parse_macro_line
from photonx_eda_pcb.parsers.gerber_parts.aperture import parse_aperture
from photonx_eda_pcb.parsers.gerber_parts.format_spec import parse_format_spec
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "numeric_tokens.gtl"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.parametrize("digit", ["١", "１"])
def test_gerber_format_helper_rejects_non_ascii_digits(digit: str):
    with pytest.raises(ValueError, match="invalid Gerber format specification"):
        parse_format_spec(f"%FSLAX{digit}4Y24*%")


@pytest.mark.parametrize("digits", ["١٠", "１０"])
def test_gerber_aperture_helper_rejects_non_ascii_identifiers(digits: str):
    with pytest.raises(ValueError, match="unsupported aperture definition"):
        parse_aperture(f"%ADD{digits}C,0.500*%")


@pytest.mark.parametrize("digit", ["١", "１"])
def test_low_level_macro_primitive_rejects_non_ascii_codes(digit: str):
    with pytest.raises(ValueError, match="invalid aperture macro primitive"):
        parse_macro_line(f"{digit},1,0.500,0,0*")


@pytest.mark.parametrize("digit", ["١", "１"])
def test_macro_substitution_rejects_non_ascii_variable_names_and_references(
    digit: str,
):
    with pytest.raises(ValueError, match="invalid macro variable name"):
        substitute("$1", {digit: 1.0})

    with pytest.raises(ValueError, match="invalid macro variable reference"):
        substitute(f"${digit}", {})


@pytest.mark.parametrize(
    "statement",
    [
        "%FSLAX٢4Y24*%",
        "%ADD١٠C,0.500*%",
        "D١٠*",
    ],
)
def test_production_parser_rejects_non_ascii_numeric_tokens(
    tmp_path: Path,
    statement: str,
):
    body = (
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.500*%\n"
        "D10*\n"
        f"{statement}\n"
        "M02*\n"
    )
    path = _write(tmp_path, body)

    with pytest.raises(UnsupportedFeatureError, match="unrecognized Gerber statement"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


@pytest.mark.parametrize("digit", ["١", "１"])
def test_production_macro_rejects_non_ascii_variable_reference(
    tmp_path: Path,
    digit: str,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        f"%AMROUND*1,1,${digit},0,0*%\n"
        "%ADD10ROUND*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="could not be evaluated"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_ascii_macro_variable_behavior_is_unchanged():
    statements = parse_macro_body("$2=$1x1.25*1,1,$2,0,0*")

    evaluated = evaluate_macro(statements, {"1": 2.0})

    assert evaluated[0]["values"] == pytest.approx([1.0, 2.5, 0.0, 0.0])
