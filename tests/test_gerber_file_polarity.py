from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(body, encoding="utf-8")
    return path


def test_positive_x2_file_polarity_is_explicitly_accepted(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TF.FilePolarity,Positive*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1
    assert any(
        diagnostic.code == "GERBER_FILE_POLARITY_POSITIVE"
        for diagnostic in result.diagnostics
    )


def test_negative_x2_file_polarity_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TF.FilePolarity,Negative*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="absence of material"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_negative_x2_file_polarity_suppresses_geometry_in_permissive_mode(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TF.FilePolarity,Negative*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X020000Y000000D03*\n"
        "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_NEGATIVE_FILE_POLARITY"
        for diagnostic in result.diagnostics
    )


def test_late_negative_file_polarity_clears_already_emitted_geometry(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        HEADER
        + "X000000Y000000D02*\n"
        + "X010000Y000000D01*\n"
        + "%TF.FilePolarity,Negative*%\n"
        + "X020000Y000000D01*\n"
        + "M02*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


def test_conflicting_file_polarity_values_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TF.FilePolarity,Positive*%\n"
        "%TF.FilePolarity,Negative*%\n"
        "M02*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="conflicting"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_invalid_file_polarity_value_is_not_treated_as_generic_metadata(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TF.FilePolarity,Unknown*%\n"
        "M02*\n",
    )

    with pytest.raises(ParseError, match="invalid X2 .FilePolarity"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_preflight_blocks_negative_x2_file_polarity(tmp_path: Path):
    path = _write(
        tmp_path,
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%TF.FilePolarity,Negative*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "M02*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert report.strict_blockers
