from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = """%FSLAX24Y24*%
%MOMM*%
%ADD10R,0.600X0.300*%
%ADD11C,0.200*%
"""


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "top.gtl"
    path.write_text(HEADER + body + "M02*\n", encoding="utf-8")
    return path


def test_strict_mode_rejects_rectangular_linear_draw(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    with pytest.raises(UnsupportedFeatureError, match="not modeled exactly"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_permissive_mode_skips_rectangular_draw_instead_of_approximating(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert any(
        diagnostic.code == "NON_CIRCULAR_DRAW"
        for diagnostic in result.diagnostics
    )


def test_skipped_noncircular_draw_still_advances_current_point(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "D11*\n"
        "X020000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert len(result.tracks) == 1
    track = result.tracks[0]
    assert (track.start.x, track.start.y) == pytest.approx((1.0, 0.0))
    assert (track.end.x, track.end.y) == pytest.approx((2.0, 0.0))
    assert track.width == pytest.approx(0.2)


def test_rectangular_flash_remains_supported(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "X010000Y020000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.pads) == 1
    pad = result.pads[0]
    assert pad.shape == "R"
    assert pad.size_x == pytest.approx(0.6)
    assert pad.size_y == pytest.approx(0.3)


def test_preflight_blocks_noncircular_draw(tmp_path: Path):
    path = _write(
        tmp_path,
        "D10*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any("NON_CIRCULAR_DRAW" in blocker for blocker in report.strict_blockers)
