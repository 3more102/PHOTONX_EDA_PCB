from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(
        "%FSLAX24Y24*%\n%MOMM*%\n" + body + "\nM02*\n",
        encoding="utf-8",
    )
    return path


def test_g74_quarter_circle_boundary_is_reconstructed(tmp_path: Path):
    path = _write(
        tmp_path,
        "g74_region.gtl",
        "G74*\n"
        "G36*\n"
        "X010000Y000000D02*\n"
        "G03*\n"
        "X000000Y010000I010000J000000D01*\n"
        "G01*\n"
        "X000000Y000000D01*\n"
        "X010000Y000000D01*\n"
        "G37*",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    region = result.regions[0]
    assert region.points[0] == region.points[-1]
    assert region_shape(region).area == pytest.approx(0.78539816339, rel=0.02)
    arc = next(
        event
        for event in region.provenance.evidence
        if event.kind == "gerber_region_arc_tessellation"
    )
    assert "quadrant_mode=single" in arc.detail
    assert "direction=CCW" in arc.detail


def test_g74_region_rejects_signed_center_distance(tmp_path: Path):
    path = _write(
        tmp_path,
        "g74_signed.gtl",
        "G74*\n"
        "G36*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n"
        "G37*",
    )

    with pytest.raises(ParseError, match="unsigned center distances"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_g74_region_permissive_center_failure_aborts_whole_region(tmp_path: Path):
    path = _write(
        tmp_path,
        "g74_missing_center.gtl",
        "G74*\n"
        "G36*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I010000D01*\n"
        "G37*",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert not result.regions
    assert any(
        diagnostic.code == "GERBER_G74_CENTER_MISSING"
        for diagnostic in result.diagnostics
    )


def test_g74_region_arc_composes_with_step_repeat(tmp_path: Path):
    path = _write(
        tmp_path,
        "g74_panel.gtl",
        "%SRX2Y1I5J0*%\n"
        "G74*\n"
        "G36*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I010000J000000D01*\n"
        "G01*\n"
        "X000000Y000000D01*\n"
        "X010000Y000000D01*\n"
        "G37*\n"
        "%SR*%",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    assert len({region.id for region in result.regions}) == 2
    assert sorted(min(point.x for point in region.points) for region in result.regions) == pytest.approx([0.0, 5.0])
