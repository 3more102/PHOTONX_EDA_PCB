from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.500*%
D10*
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "panel.gtl"
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("statement", "message"),
    [
        ("%SRX2Y1IBADJ0*%", "invalid Gerber step-and-repeat"),
        ("%SRX0Y1I10J0*%", "counts must be positive"),
        ("%SRX101Y100I10J10*%", "limit is"),
    ],
)
def test_invalid_step_repeat_fails_closed_in_strict_mode(
    tmp_path: Path,
    statement: str,
    message: str,
):
    path = _write(
        tmp_path,
        statement + "\n"
        "X010000Y010000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match=message):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


@pytest.mark.parametrize(
    ("statement", "expected_code"),
    [
        ("%SRX2Y1IBADJ0*%", "INVALID_GERBER_STEP_REPEAT"),
        ("%SRX0Y1I10J0*%", "INVALID_GERBER_STEP_REPEAT"),
        ("%SRX101Y100I10J10*%", "GERBER_STEP_REPEAT_LIMIT"),
    ],
)
def test_invalid_step_repeat_suppresses_permissive_file_geometry(
    tmp_path: Path,
    statement: str,
    expected_code: str,
):
    path = _write(
        tmp_path,
        "X005000Y005000D03*\n"
        + statement
        + "\n"
        "X010000Y010000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(
        diagnostic.code == expected_code
        for diagnostic in result.diagnostics
    )


def test_step_repeat_termination_does_not_reenable_after_invalid_state(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%SRX0Y1I10J0*%\n"
        "%SR*%\n"
        "X010000Y010000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert result.tracks == []
    assert result.outline == []


def test_valid_step_repeat_still_expands_supported_geometry(tmp_path: Path):
    path = _write(
        tmp_path,
        "%SRX2Y1I10J0*%\n"
        "X010000Y010000D03*\n"
        "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 2
    assert result.pads[0].center.x == pytest.approx(1.0)
    assert result.pads[1].center.x == pytest.approx(11.0)


@pytest.mark.parametrize(
    ("statement", "expected_code"),
    [
        ("%SRX0Y1I10J0*%", "INVALID_GERBER_STEP_REPEAT"),
        ("%SRX101Y100I10J10*%", "GERBER_STEP_REPEAT_LIMIT"),
    ],
)
def test_preflight_blocks_invalid_step_repeat(
    tmp_path: Path,
    statement: str,
    expected_code: str,
):
    path = _write(
        tmp_path,
        statement + "\n"
        "X010000Y010000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(expected_code in blocker for blocker in report.strict_blockers)
