from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.gerber_image import polygonize_track
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


def test_lpc_region_subtracts_exact_hole(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_hole.gtl",
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(84.0)
    assert "gerber_layer_polarity_composition" in {
        evidence.kind for evidence in result.regions[0].provenance.evidence
    }


def test_lpc_order_allows_dark_refill_inside_cleared_area(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_refill.gtl",
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000")
        + "%LPD*%\n"
        + _rectangle("040000", "040000", "060000", "060000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    assert sum(region_shape(region).area for region in result.regions) == pytest.approx(
        88.0
    )
    assert sorted(len(region.holes) for region in result.regions) == [0, 1]


def test_lpc_clear_before_dark_does_not_erase_future_material(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_clear_first.gtl",
        "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000")
        + "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    assert result.regions[0].holes == ()
    assert region_shape(result.regions[0]).area == pytest.approx(100.0)


def test_lpc_can_split_one_dark_region_into_two_components(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_split.gtl",
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("040000", "-010000", "060000", "110000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    assert sum(region_shape(region).area for region in result.regions) == pytest.approx(
        80.0
    )
    assert [region.points[0].x for region in result.regions] == pytest.approx(
        [0.0, 6.0]
    )


def test_lpc_region_composition_has_deterministic_ids(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_ids.gtl",
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000"),
    )

    first = GerberRS274XParser("F.Cu", strict=True).parse(path)
    second = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert [region.id for region in first.regions] == [
        region.id for region in second.regions
    ]


def test_lpc_region_only_file_is_preflight_ready(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_preflight.gtl",
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000"),
    )

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_lpc_clear_linear_track_before_material_is_supported_noop(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_track.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "%LPC*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.regions == []
    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_lpc_clear_linear_track_subtracts_capsule_from_dark_region(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_clear_track.gtl",
        "%ADD10C,2.000*%\n"
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "D10*\n"
        "%LPC*%\n"
        "X020000Y050000D02*\n"
        "X080000Y050000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    clear_shape = polygonize_track(2.0, 5.0, 8.0, 5.0, 2.0).geometry
    assert result.tracks == []
    assert len(result.regions) == 1
    assert len(result.regions[0].holes) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(
        100.0 - clear_shape.area
    )
    assert any(
        evidence.kind == "gerber_track_polygonization"
        and "method=capsule_inscribed_chords" in evidence.detail
        and "max_chord_error_mm=0.005" in evidence.detail
        for evidence in result.regions[0].provenance.evidence
    )


def test_lpc_clear_circular_flash_before_material_is_supported_noop(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_flash.gtl",
        "%ADD10C,0.500*%\n"
        "D10*\n"
        "%LPC*%\n"
        "X050000Y050000D03*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.pads == []
    assert result.regions == []
    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_lpc_mixed_dark_track_and_clear_region_preserves_track_material(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_mixed.gtl",
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "%LPD*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%LPC*%\n"
        + _rectangle("030000", "030000", "070000", "070000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    expected = polygonize_track(0.0, 0.0, 1.0, 0.0, 0.2).geometry
    assert result.tracks == []
    assert len(result.regions) == 1
    assert region_shape(result.regions[0]).area == pytest.approx(expected.area)
    assert any(
        evidence.kind == "gerber_track_polygonization"
        for evidence in result.regions[0].provenance.evidence
    )

    report = preflight(path)
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_lpc_tessellated_arc_track_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "lpc_arc_track.gtl",
        "%ADD10R,10X10*%\n"
        "%ADD11C,0.200*%\n"
        "%LPD*%\n"
        "D10*\n"
        "X050000Y050000D03*\n"
        "D11*\n"
        "%LPC*%\n"
        "G75*\n"
        "X060000Y050000D02*\n"
        "G03X050000Y060000I-010000J000000D01*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="tessellated arc tracks or outline geometry",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    report = preflight(path)
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_CLEAR_POLARITY_NON_POLYGONAL_GEOMETRY" in blocker
        for blocker in report.strict_blockers
    )
