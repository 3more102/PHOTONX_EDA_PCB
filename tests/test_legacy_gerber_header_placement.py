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


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("command", "error_text"),
    [
        ("%MIA1*%", "must precede"),
        ("%SFA2B2*%", "must precede"),
        ("%OFA1B0*%", "must precede"),
        ("%IR90*%", "must precede"),
    ],
)
def test_d02_coordinate_closes_legacy_image_header_in_strict_mode(
    tmp_path: Path,
    command: str,
    error_text: str,
):
    path = _write(
        tmp_path,
        "late_transform_after_move.gtl",
        "X010000Y020000D02*\n"
        + command
        + "\n"
        + "X020000Y020000D03*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match=error_text):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


@pytest.mark.parametrize(
    ("command", "diagnostic"),
    [
        ("%MIA1*%", "LATE_GERBER_MIRROR_IMAGE"),
        ("%SFA2B2*%", "LATE_GERBER_SCALE_FACTOR"),
        ("%OFA1B0*%", "LATE_GERBER_OFFSET"),
        ("%IR90*%", "LATE_GERBER_IMAGE_ROTATION"),
        ("%IPPOS*%", "LATE_GERBER_IMAGE_POLARITY"),
    ],
)
def test_d02_coordinate_late_transform_suppresses_permissive_geometry(
    tmp_path: Path,
    command: str,
    diagnostic: str,
):
    path = _write(
        tmp_path,
        "late_transform_permissive.gtl",
        "X010000Y020000D02*\n"
        + command
        + "\n"
        + "X020000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert any(d.code == diagnostic for d in result.diagnostics)


@pytest.mark.parametrize(
    ("command", "diagnostic"),
    [
        ("%MIA1*%", "LATE_GERBER_MIRROR_IMAGE"),
        ("%SFA2B2*%", "LATE_GERBER_SCALE_FACTOR"),
        ("%OFA1B0*%", "LATE_GERBER_OFFSET"),
        ("%IR90*%", "LATE_GERBER_IMAGE_ROTATION"),
        ("%ASAYBX*%", "LATE_GERBER_AXIS_SELECT"),
        ("%INLateName*%", "LATE_GERBER_IMAGE_NAME"),
        ("%IPPOS*%", "LATE_GERBER_IMAGE_POLARITY"),
    ],
)
def test_preflight_blocks_header_commands_after_d02(
    tmp_path: Path,
    command: str,
    diagnostic: str,
):
    path = _write(
        tmp_path,
        "late_header_preflight.gtl",
        "X010000Y020000D02*\n"
        + command
        + "\n"
        + "X020000Y020000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(diagnostic in blocker for blocker in report.strict_blockers)


@pytest.mark.parametrize(
    ("first", "second", "diagnostic"),
    [
        ("%MIA1*%", "%MIB1*%", "DUPLICATE_GERBER_MIRROR_IMAGE"),
        ("%SFA2B2*%", "%SFA1B1*%", "DUPLICATE_GERBER_SCALE_FACTOR"),
        ("%OFA1B0*%", "%OFA0B1*%", "DUPLICATE_GERBER_OFFSET"),
        ("%IR90*%", "%IR180*%", "DUPLICATE_GERBER_IMAGE_ROTATION"),
        ("%ASAXBY*%", "%ASAYBX*%", "DUPLICATE_GERBER_AXIS_SELECT"),
        ("%INOne*%", "%INTwo*%", "DUPLICATE_GERBER_IMAGE_NAME"),
        ("%IPPOS*%", "%IPPOS*%", "DUPLICATE_GERBER_IMAGE_POLARITY"),
    ],
)
def test_preflight_blocks_duplicate_header_commands(
    tmp_path: Path,
    first: str,
    second: str,
    diagnostic: str,
):
    path = _write(
        tmp_path,
        "duplicate_header_preflight.gtl",
        first + "\n" + second + "\n" + "X000000Y000000D03*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(diagnostic in blocker for blocker in report.strict_blockers)


def test_late_image_name_is_strictly_invalid_even_though_non_geometric(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "late_in.gtl",
        "X010000Y020000D02*\n"
        "%INLateName*%\n"
        "X020000Y020000D03*\n",
    )

    with pytest.raises(ParseError, match="must appear before"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_late_positive_image_polarity_is_strictly_invalid(tmp_path: Path):
    path = _write(
        tmp_path,
        "late_ippos.gtl",
        "X010000Y020000D02*\n"
        "%IPPOS*%\n"
        "X020000Y020000D03*\n",
    )

    with pytest.raises(ParseError, match="must appear before"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_header_commands_before_first_coordinate_remain_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "valid_header.gtl",
        "%IPPOS*%\n"
        "%ASAYBX*%\n"
        "%INBoardTop*%\n"
        "%MIA1*%\n"
        "%SFA2B2*%\n"
        "%OFA1B-1*%\n"
        "%IR90*%\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    # (1,2) -> MI (-1,2) -> SF (-2,4) -> OF (-1,3) -> IR90 (-3,-1)
    assert (result.pads[0].center.x, result.pads[0].center.y) == pytest.approx(
        (-3.0, -1.0)
    )
