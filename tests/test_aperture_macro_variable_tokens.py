from pathlib import Path

import pytest

from photonx_eda_pcb.aperture_macros.variables import substitute
from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "macro-variable-tokens.gtl"
    path.write_text(text, encoding="utf-8")
    return path


def test_substitute_keeps_undefined_longer_variable_intact():
    assert substitute("$10+$1", {"1": 2.5}) == "$10+2.5"


def test_substitute_replaces_exact_overlapping_variable_tokens():
    assert substitute("$10+$1", {"1": 2.5, "10": 7.0}) == "7.0+2.5"


def test_substitute_accepts_dollar_prefixed_variable_keys():
    assert substitute("$1+$2", {"$1": 3.0, "$2": 4.0}) == "3.0+4.0"


def test_undefined_longer_macro_variable_fails_closed_end_to_end(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%AMROUND*1,1,$10,0,0*%\n"
        "%ADD10ROUND,0.800*%\n"
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
