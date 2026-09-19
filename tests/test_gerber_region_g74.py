from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text("%FSLAX24Y24*%\n%MOMM*%\n" + body + "\nM02*\n", encoding="utf-8")
    return path


def test_g74_quarter_circle_region_boundary(tmp_path: Path):
    path = _write(tmp_path, "g74.gtl",
        "G74*\nG36*\nX010000Y000000D02*\nG03*\n"
        "X000000Y010000I010000J000000D01*\nG01*\n"
        "X000000Y000000D01*\nX010000Y000000D01*\nG37*")
    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(0.78539816339, rel=0.02)
    ev = next(e for e in result.regions[0].provenance.evidence if e.kind == "gerber_region_arc_tessellation")
    assert "quadrant_mode=single" in ev.detail


def test_g74_region_signed_offsets_fail_closed(tmp_path: Path):
    path = _write(tmp_path, "signed.gtl",
        "G74*\nG36*\nX010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\nG37*")
    with pytest.raises(ParseError, match="unsigned center distances"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_g74_region_requires_both_center_distances(tmp_path: Path):
    path = _write(tmp_path, "missing.gtl",
        "G74*\nG36*\nX010000Y000000D02*\n"
        "G03X000000Y010000I010000D01*\nG37*")
    with pytest.raises(ParseError, match="require both unsigned I and J"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_g74_region_permissive_center_failure_emits_no_partial_region(tmp_path: Path):
    path = _write(tmp_path, "permissive.gtl",
        "G74*\nG36*\nX010000Y000000D02*\n"
        "G03X000000Y010000I010000D01*\nG37*")
    result = GerberRS274XParser("F.Cu", strict=False).parse(path)
    assert not result.regions
    assert any(d.code == "GERBER_G74_CENTER_MISSING" for d in result.diagnostics)


def test_g74_region_composes_with_step_repeat(tmp_path: Path):
    path = _write(tmp_path, "panel.gtl",
        "%SRX2Y1I5J0*%\nG74*\nG36*\nX010000Y000000D02*\n"
        "G03X000000Y010000I010000J000000D01*\nG01*\n"
        "X000000Y000000D01*\nX010000Y000000D01*\nG37*\n%SR*%")
    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    assert len(result.regions) == 2
    assert len({r.id for r in result.regions}) == 2


def test_g74_region_sweep_over_90_degrees_is_rejected(tmp_path: Path):
    path = _write(tmp_path, "over90.gtl",
        "G74*\nG36*\nX020000Y000000D02*\n"
        "G03X000000Y000000I010000J000000D01*\nG37*")
    with pytest.raises(ParseError, match="no G74 center candidate"):
        GerberRS274XParser("F.Cu", strict=True).parse(path)
