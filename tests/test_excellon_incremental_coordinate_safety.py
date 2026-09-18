from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.excellon import ExcellonParser
from photonx_eda_pcb.preflight import preflight


HEADER = """M48
METRIC
T01C0.600
%
T01
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.drl"
    path.write_text(HEADER + body + "M30\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_incremental_excellon_modes_fail_closed_in_strict_mode(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000\n"
        "X1.000Y0.000\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="incremental Excellon coordinates are unsupported",
    ):
        ExcellonParser(strict=True).parse(path)


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_incremental_excellon_modes_suppress_permissive_geometry(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000\n"
        "X1.000Y0.000\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []
    assert any(
        diagnostic.code == "UNSUPPORTED_EXCELLON_INCREMENTAL"
        for diagnostic in result.diagnostics
    )


@pytest.mark.parametrize("command", ["ICI,OFF", "G90"])
def test_explicit_absolute_excellon_modes_remain_supported(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000\n"
        "X2.000Y1.000\n",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert len(result.drills) == 2
    assert result.drills[0].center.x == pytest.approx(1.0)
    assert result.drills[1].center.x == pytest.approx(2.0)


def test_late_incremental_mode_clears_prior_geometry_and_absolute_does_not_reenable(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "X1.000Y1.000\n"
        "ICI,ON\n"
        "X1.000Y0.000\n"
        "ICI,OFF\n"
        "X3.000Y1.000\n",
    )

    result = ExcellonParser(strict=False).parse(path)

    assert result.drills == []
    assert result.slots == []
    assert result.routes == []


@pytest.mark.parametrize("command", ["ICI,ON", "G91"])
def test_preflight_blocks_incremental_excellon_modes(
    tmp_path: Path,
    command: str,
):
    path = _write(
        tmp_path,
        command + "\n"
        "X1.000Y1.000\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_EXCELLON_INCREMENTAL" in blocker
        for blocker in report.strict_blockers
    )
