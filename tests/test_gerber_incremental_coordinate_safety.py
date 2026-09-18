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


@pytest.mark.parametrize("command", ["G91*", "G091*"])
def test_incremental_coordinate_mode_fails_closed_in_strict_mode(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X010000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="incremental coordinate mode is not implemented",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_incremental_mode_suppresses_permissive_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "G91*\n"
        "X010000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED"
        for diagnostic in result.diagnostics
    )


def test_late_incremental_mode_clears_prior_geometry_and_g90_does_not_reenable(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "G90*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "G91*\n"
        "X010000Y000000D01*\n"
        "G90*\n"
        "X030000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []


def test_explicit_absolute_mode_remains_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "G90*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 1


def test_preflight_blocks_incremental_coordinate_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "G91*\n"
        "X010000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED" in blocker
        for blocker in report.strict_blockers
    )
