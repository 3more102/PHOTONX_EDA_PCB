from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
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


def test_linear_region_is_supported_without_leaking_tracks(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X010000Y010000D01*\n"
        "X000000Y010000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert len(result.regions) == 1


def test_aperture_block_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ABD11*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%AB*%\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="supported aperture-block subset accepts only one",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_block_body_does_not_leak_geometry_in_permissive_mode(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%ABD11*%\n"
        "X010000Y010000D03*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%AB*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.regions == []
    assert result.outline == []
    assert any(
        diagnostic.code == "UNSUPPORTED_GERBER_APERTURE_BLOCK"
        for diagnostic in result.diagnostics
    )


def test_supported_region_does_not_disable_surrounding_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "G36*\n"
        "X020000Y000000D02*\n"
        "X030000Y000000D01*\n"
        "X030000Y010000D01*\n"
        "X020000Y000000D01*\n"
        "G37*\n"
        "X040000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 2
    assert len(result.regions) == 1
    assert result.pads == []
    assert result.outline == []


def test_preflight_accepts_supported_linear_region(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X010000Y010000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert report.strict_blockers == []


def test_preflight_still_blocks_aperture_blocks(tmp_path: Path):
    path = _write(tmp_path, "%ABD11*%\n%AB*%\n")

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_APERTURE_BLOCK" in blocker
        for blocker in report.strict_blockers
    )
