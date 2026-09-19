from pathlib import Path

import pytest

from photonx_eda_pcb.geometry_kernel import region_shape
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser


HEADER = "%FSLAX24Y24*%\n%MOMM*%\n"


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


def _write(directory: Path, body: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "top.gtl"
    path.write_text(HEADER + body + "M02*\n", encoding="utf-8")
    return path


def _composition_detail(region) -> str:
    return next(
        evidence.detail
        for evidence in region.provenance.evidence
        if evidence.kind == "gerber_layer_polarity_composition"
    )


def test_lpc_composed_component_provenance_is_spatially_local(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("020000", "020000", "040000", "040000")
        + "%LPD*%\n"
        + _rectangle("200000", "000000", "300000", "100000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)
    left, right = sorted(
        result.regions,
        key=lambda region: min(point.x for point in region.points),
    )

    assert len(result.regions) == 2
    assert region_shape(left).area == pytest.approx(96.0)
    assert region_shape(right).area == pytest.approx(100.0)

    left_sources = {source.raw for source in left.provenance.sources}
    right_sources = {source.raw for source in right.provenance.sources}

    assert "%LPC*%" in left_sources
    assert "X000000Y000000D02*" in left_sources
    assert "X200000Y000000D02*" not in left_sources

    assert "%LPC*%" not in right_sources
    assert "X000000Y000000D02*" not in right_sources
    assert "X200000Y000000D02*" in right_sources

    assert "relevant_operations=2" in _composition_detail(left)
    assert "relevant_operations=1" in _composition_detail(right)


def test_lpc_component_id_is_stable_when_unrelated_material_is_added(tmp_path: Path):
    common = (
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("020000", "020000", "040000", "040000")
    )
    base = _write(tmp_path / "base", common)
    extended = _write(
        tmp_path / "extended",
        common
        + "%LPD*%\n"
        + _rectangle("200000", "000000", "300000", "100000"),
    )

    base_result = GerberRS274XParser("F.Cu", strict=True).parse(base)
    extended_result = GerberRS274XParser("F.Cu", strict=True).parse(extended)

    assert len(base_result.regions) == 1
    left_extended = min(
        extended_result.regions,
        key=lambda region: min(point.x for point in region.points),
    )

    assert base_result.regions[0].id == left_extended.id
    assert region_shape(base_result.regions[0]).equals(region_shape(left_extended))


def test_point_only_clear_contact_does_not_claim_component_provenance(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("100000", "100000", "120000", "120000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 1
    region = result.regions[0]
    assert region_shape(region).area == pytest.approx(100.0)
    assert "%LPC*%" not in {source.raw for source in region.provenance.sources}
    assert "relevant_operations=1" in _composition_detail(region)

def test_lpc_refill_component_excludes_erased_dark_provenance(tmp_path: Path):
    path = _write(
        tmp_path,
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("020000", "020000", "080000", "080000")
        + "%LPD*%\n"
        + _rectangle("040000", "040000", "060000", "060000"),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.regions) == 2
    outer = max(result.regions, key=lambda region: region_shape(region).area)
    refill = min(result.regions, key=lambda region: region_shape(region).area)
    assert region_shape(outer).area == pytest.approx(64.0)
    assert region_shape(refill).area == pytest.approx(4.0)

    outer_sources = {source.raw for source in outer.provenance.sources}
    refill_sources = {source.raw for source in refill.provenance.sources}

    assert "X000000Y000000D02*" in outer_sources
    assert "X020000Y020000D02*" in outer_sources
    assert "X040000Y040000D02*" not in outer_sources

    assert "X040000Y040000D02*" in refill_sources
    assert "X000000Y000000D02*" not in refill_sources
    assert "X020000Y020000D02*" not in refill_sources
    assert "%LPC*%" not in refill_sources

    assert "effective_operations=3" in _composition_detail(outer)
    assert "relevant_operations=2" in _composition_detail(outer)
    assert "effective_operations=3" in _composition_detail(refill)
    assert "relevant_operations=1" in _composition_detail(refill)


def test_lpc_redundant_dark_region_does_not_pollute_provenance_or_id(tmp_path: Path):
    base_body = (
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + "%LPC*%\n"
        + _rectangle("200000", "200000", "210000", "210000")
    )
    redundant_body = (
        "%LPD*%\n"
        + _rectangle("000000", "000000", "100000", "100000")
        + _rectangle("020000", "020000", "040000", "040000")
        + "%LPC*%\n"
        + _rectangle("200000", "200000", "210000", "210000")
    )

    base = _write(tmp_path / "base", base_body)
    redundant = _write(tmp_path / "redundant", redundant_body)

    base_region = GerberRS274XParser("F.Cu", strict=True).parse(base).regions[0]
    redundant_region = GerberRS274XParser("F.Cu", strict=True).parse(redundant).regions[0]

    assert region_shape(base_region).equals(region_shape(redundant_region))
    assert base_region.id == redundant_region.id
    redundant_sources = {source.raw for source in redundant_region.provenance.sources}
    assert "X020000Y020000D02*" not in redundant_sources
    assert "relevant_operations=1" in _composition_detail(redundant_region)

