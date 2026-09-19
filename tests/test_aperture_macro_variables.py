from pathlib import Path

import pytest

from photonx_eda_pcb.aperture_macros import evaluate_macro, parse_macro_body
from photonx_eda_pcb.aperture_macros.validation import validate_macro
from photonx_eda_pcb.aperture_macros.variables import substitute
from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "macro_variables.gtl"
    path.write_text(text, encoding="utf-8")
    return path


def test_macro_variable_definition_is_evaluated_in_source_order():
    statements = parse_macro_body("$3=$1x1.25*$4=$3+$2*1,1,$4,0,0")

    evaluated = evaluate_macro(statements, {"1": 2.0, "2": 0.5})

    assert len(evaluated) == 1
    assert evaluated[0]["kind"] == "circle"
    assert evaluated[0]["values"] == pytest.approx([1.0, 3.0, 0.0, 0.0])


def test_undefined_macro_variables_default_to_zero_without_prefix_aliasing():
    statements = parse_macro_body("$4=$9+2*1,1,$4+$8,0,0")

    evaluated = evaluate_macro(statements)

    assert evaluated[0]["values"] == pytest.approx([1.0, 2.0, 0.0, 0.0])
    assert substitute("$10+$1", {"1": 2.5}) == "0.0+2.5"
    assert substitute("$10+$1", {"1": 2.5, "10": 7.0}) == "7.0+2.5"


def test_macro_variable_definition_cannot_redefine_ad_parameter():
    statements = parse_macro_body("$1=$1x2*1,1,$1,0,0")

    with pytest.raises(ValueError, match=r"\$1 cannot be redefined"):
        evaluate_macro(statements, {"1": 1.0})


def test_macro_variable_definition_cannot_redefine_prior_definition():
    statements = parse_macro_body("$4=1*$4=2*1,1,$4,0,0")

    with pytest.raises(ValueError, match=r"\$4 cannot be redefined"):
        evaluate_macro(statements)


def test_macro_variable_zero_index_is_invalid():
    with pytest.raises(ValueError, match="invalid macro variable definition"):
        parse_macro_body("$0=1*1,1,1,0,0")

    statements = parse_macro_body("1,1,$0+1,0,0")
    with pytest.raises(ValueError, match="positive integer"):
        evaluate_macro(statements)


def test_production_parser_supports_macro_variable_definition(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMVARDIAM*$2=$1x1.25*1,1,$2,0,0*%\n"
        "%ADD10VARDIAM,2.0*%\n"
        "D10*\n"
        "X010000Y020000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "C"
    assert pad.center.x == pytest.approx(1.0)
    assert pad.center.y == pytest.approx(2.0)
    assert pad.size_x == pytest.approx(2.5)
    assert pad.size_y == pytest.approx(2.5)

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_production_parser_uses_zero_for_undefined_macro_variable(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMDEFAULT*$3=$7+1.5*1,1,$3,0,0*%\n"
        "%ADD10DEFAULT*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    assert result.pads[0].size_x == pytest.approx(1.5)


def test_production_parser_rejects_macro_variable_redefinition(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMBROKEN*$1=$1x2*1,1,$1,0,0*%\n"
        "%ADD10BROKEN,1.0*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="could not be evaluated"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )


def test_circle_macro_extra_modifier_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMROUND*1,1,0.800,0,0,0,123*%\n"
        "%ADD10ROUND*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="requires four or five modifiers",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )


@pytest.mark.parametrize(
    ("exposure", "diameter", "center_x", "center_y", "rotation"),
    [
        ("1e309", "0.800", "0", "0", "0"),
        ("1", "1e309-1e309", "0", "0", "0"),
        ("1", "0.800", "0", "0", "1e309"),
    ],
)
def test_circle_macro_nonfinite_values_fail_closed(
    tmp_path: Path,
    exposure: str,
    diameter: str,
    center_x: str,
    center_y: str,
    rotation: str,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        f"%AMROUND*1,{exposure},{diameter},{center_x},{center_y},{rotation}*%\n"
        "%ADD10ROUND*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="requires finite modifiers"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )


def test_circle_macro_unit_conversion_overflow_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%AMROUND*1,1,1e308,0,0*%\n"
        "%ADD10ROUND*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="overflows after active-unit conversion"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_validate_macro_accepts_variable_definition_statements():
    statements = parse_macro_body("$2=1*1,1,$2,0,0")

    assert validate_macro(statements) == []


def test_macro_assignment_integer_overflow_fails_closed(tmp_path: Path):
    huge_integer = "9" * 400
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        f"%AMOVERFLOW*$2={huge_integer}*1,1,$2,0,0*%\n"
        "%ADD10OVERFLOW*%\n"
        "D10*\n"
        "X000000Y000000D03*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="could not be evaluated"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_APERTURE_MACRO" in blocker
        for blocker in report.strict_blockers
    )
