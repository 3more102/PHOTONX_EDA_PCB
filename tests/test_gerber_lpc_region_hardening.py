from pathlib import Path

import pytest

from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.preflight import preflight


HEADER = "%FSLAX24Y24*%\n%MOMM*%\n"


def _write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(HEADER + body + "M02*\n", encoding="utf-8")
    return path


def _rectangle(x0: str, y0: str, x1: str, y1: str) -> str:
    return (
        "G36*\n"
        f"X{x0}Y{y0}D02*\n"
        f"X{x1}Y{y0}D01*\n"
        f"X{x1}Y{y1}D01*\n"
        f"X{x0}Y{y1}D01*\n"
        f"X{x0}Y{y0}D01*\n"
        "G37*\n"
    )


def test_lpc_composition_respects_step_repeat_instances(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_sr.gtl",
        "%SRX2Y1I20J0*%\n"
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000")
        + "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    assert all(len(region.holes) == 1 for region in result.regions)
    assert sum(region_shape(region).area for region in result.regions) == pytest.approx(
        168.0
    )
    assert sorted(min(point.x for point in region.points) for region in result.regions) == pytest.approx(
        [0.0, 20.0]
    )

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_lpc_composition_follows_whole_image_mirror_and_rotation(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_transform.gtl",
        "%MIA1*%\n"
        "%IR90*%\n"
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(84.0)
    evidence = {event.kind for event in result.regions[0].provenance.evidence}
    assert "gerber_layer_polarity_composition" in evidence


def test_lpc_multicontour_clear_statement_materializes_two_holes(tmp_path: Path):
    clear_two_contours = (
        "G36*\n"
        "X020000Y020000D02*\n"
        "X040000Y020000D01*\n"
        "X040000Y040000D01*\n"
        "X020000Y040000D01*\n"
        "X020000Y020000D01*\n"
        "X080000Y080000D02*\n"
        "X100000Y080000D01*\n"
        "X100000Y100000D01*\n"
        "X080000Y100000D01*\n"
        "X080000Y080000D01*\n"
        "G37*\n"
    )
    path = _write(
        tmp_path,
        "lpc_multicontour.gtl",
        "%LPD*%\n"
        + _rectangle("000000", "000000", "120000", "120000")
        + "%LPC*%\n"
        + clear_two_contours,
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 2
    assert region_shape(result.regions[0]).area == pytest.approx(136.0)


def test_lpc_clear_region_hole_preserves_dark_island(tmp_path: Path):
    clear_with_cut_in_hole = (
        "G36*\n"
        "X020000Y020000D02*\n"
        "X080000Y020000D01*\n"
        "X080000Y080000D01*\n"
        "X020000Y080000D01*\n"
        "X020000Y050000D01*\n"
        "X040000Y050000D01*\n"
        "X040000Y060000D01*\n"
        "X060000Y060000D01*\n"
        "X060000Y040000D01*\n"
        "X040000Y040000D01*\n"
        "X040000Y050000D01*\n"
        "X020000Y050000D01*\n"
        "X020000Y020000D01*\n"
        "G37*\n"
    )
    path = _write(
        tmp_path,
        "lpc_clear_hole.gtl",
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + clear_with_cut_in_hole,
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    assert sum(region_shape(region).area for region in result.regions) == pytest.approx(
        68.0
    )
    assert sorted(len(region.holes) for region in result.regions) == [0, 1]
    assert any(
        event.kind == "gerber_region_cut_in"
        for region in result.regions
        for event in region.provenance.evidence
    )
