from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
"""


def _write(tmp_path: Path, aperture: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(
        HEADER
        + aperture
        + "\nD10*\n"
        + "X010000Y020000D03*\n"
        + "M02*\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "definition",
    [
        "%ADD10R,0X0.250*%",
        "%ADD10R,0.500X0*%",
        "%ADD10O,0X0.250*%",
        "%ADD10O,0.500X0*%",
    ],
)
def test_rectangle_and_obround_require_positive_xy_sizes(
    tmp_path: Path,
    definition: str,
):
    path = _write(tmp_path, definition)

    with pytest.raises(ParseError, match="X/Y sizes must both be positive"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_invalid_obround_size_is_skipped_in_permissive_mode(tmp_path: Path):
    path = _write(tmp_path, "%ADD10O,0.500X0*%")

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.pads == []
    assert any(
        diagnostic.code == "INVALID_GERBER_STANDARD_APERTURE_SIZE"
        for diagnostic in result.diagnostics
    )
    assert any(
        diagnostic.code == "GERBER_APERTURE_GEOMETRY_SKIPPED"
        for diagnostic in result.diagnostics
    )


def test_invalid_outer_size_wins_over_unsupported_hole_semantics(tmp_path: Path):
    path = _write(tmp_path, "%ADD10R,0X0.500X0.100*%")

    with pytest.raises(ParseError, match="X/Y sizes must both be positive"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_preflight_blocks_invalid_standard_aperture_size(tmp_path: Path):
    path = _write(tmp_path, "%ADD10R,0.500X0*%")

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "INVALID_GERBER_STANDARD_APERTURE_SIZE" in blocker
        for blocker in report.strict_blockers
    )
