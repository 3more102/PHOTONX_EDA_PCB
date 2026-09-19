from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


def test_dark_layer_polarity_keeps_supported_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPD*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1


def test_clear_layer_polarity_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPC*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="tracks or outline geometry"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_clear_layer_polarity_suppresses_geometry_in_permissive_mode(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%LPC*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_CLEAR_POLARITY_NON_POLYGONAL_GEOMETRY"
        for diagnostic in result.diagnostics
    )


def test_late_clear_polarity_clears_prior_geometry_and_never_reenables(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%LPC*%\n"
        "X020000Y000000D01*\n"
        "%LPD*%\n"
        "X030000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


def test_malformed_layer_polarity_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPX*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(ParseError, match="invalid Gerber LP layer-polarity"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_malformed_layer_polarity_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPX*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert any(
        diagnostic.code == "INVALID_GERBER_LAYER_POLARITY"
        for diagnostic in result.diagnostics
    )


def test_preflight_blocks_clear_layer_polarity(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPC*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_CLEAR_POLARITY_NON_POLYGONAL_GEOMETRY" in blocker
        for blocker in report.strict_blockers
    )
