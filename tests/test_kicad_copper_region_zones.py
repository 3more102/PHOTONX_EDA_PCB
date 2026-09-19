from pathlib import Path

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, CopperRegion, NetGroup, Point


def _square(
    region_id: str = "R1",
    *,
    layer: str = "F.Cu",
    net_id: str | None = None,
    holes=(),
) -> CopperRegion:
    return CopperRegion(
        region_id,
        (
            Point(0, 0),
            Point(2, 0),
            Point(2, 1),
            Point(0, 1),
            Point(0, 0),
        ),
        layer,
        net_id=net_id,
        holes=holes,
    )


def test_simple_copper_region_exports_as_zone_with_saved_fill(tmp_path: Path):
    region = _square(net_id="N1")
    board = BoardModel(
        regions=[region],
        nets=[NetGroup("N1", ["R1"], 1.0, label='GND "A"\nB')],
    )

    path, report = export_kicad_with_report(board, tmp_path / "region.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 1
    assert report.exported_region_ids == ["R1"]
    assert report.skipped_regions == 0
    assert "(zone" in text
    assert "(net 1)" in text
    assert '(net_name "GND \\"A\\"\\nB")' in text
    assert '(layer "F.Cu")' in text
    assert '(name "PHOTONX:R1")' in text
    assert "(hatch edge 0.500000)" in text
    assert "(connect_pads (clearance 0.500000))" in text
    assert "(min_thickness 0.250000)" in text
    assert "(fill yes " in text
    assert "(island_removal_mode 1)" in text
    assert '(filled_polygon (layer "F.Cu")' in text
    assert any(
        issue.code == "KICAD_COPPER_REGION_ZONE_RULES_DEFAULTED"
        and issue.object_id == "R1"
        for issue in report.issues
    )

    # PhotonX regions are explicitly closed; KiCad polygon point lists need only
    # the corner vertices. The first point therefore appears once in the zone
    # outline and once in the saved fill, not twice per ring.
    assert text.count("(xy 0.000000 0.000000)") == 2


def test_unnetted_copper_region_exports_on_net_zero(tmp_path: Path):
    path, report = export_kicad_with_report(
        BoardModel(regions=[_square()]),
        tmp_path / "unnetted_region.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 1
    assert report.skipped_regions == 0
    assert "(net 0)" in text
    assert '(net_name "")' in text


def test_region_with_hole_exports_exact_zone_boundary_without_cached_fill(tmp_path: Path):
    hole = (
        Point(0.5, 0.25),
        Point(1.5, 0.25),
        Point(1.5, 0.75),
        Point(0.5, 0.75),
        Point(0.5, 0.25),
    )
    region = _square(holes=(hole,))

    path, report = export_kicad_with_report(
        BoardModel(regions=[region]),
        tmp_path / "hole_region.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 1
    assert report.exported_region_ids == ["R1"]
    assert report.skipped_regions == 0
    assert "(zone" in text
    assert text.count("(polygon (pts") == 2
    assert "(xy 0.500000 0.250000)" in text
    assert "(filled_polygon" not in text
    assert "    (fill)\n" in text
    assert any(
        issue.code == "KICAD_COPPER_REGION_HOLED_FILL_OMITTED"
        and issue.object_id == "R1"
        for issue in report.issues
    )


def test_region_with_invalid_hole_is_reported_and_not_exported(tmp_path: Path):
    outside_hole = (
        Point(3.0, 0.25),
        Point(4.0, 0.25),
        Point(4.0, 0.75),
        Point(3.0, 0.75),
        Point(3.0, 0.25),
    )
    region = _square(holes=(outside_hole,))

    path, report = export_kicad_with_report(
        BoardModel(regions=[region]),
        tmp_path / "invalid_hole_region.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 0
    assert report.skipped_regions == 1
    assert report.skipped_region_ids == ["R1"]
    assert "(zone" not in text
    assert any(
        issue.code == "KICAD_COPPER_REGION_INVALID_GEOMETRY"
        and issue.object_id == "R1"
        for issue in report.issues
    )


def test_region_with_unknown_net_is_reported_and_not_relabelled_net_zero(tmp_path: Path):
    region = _square(net_id="MISSING")

    path, report = export_kicad_with_report(
        BoardModel(regions=[region]),
        tmp_path / "unknown_net_region.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 0
    assert report.skipped_regions == 1
    assert "(zone" not in text
    assert any(
        issue.code == "KICAD_COPPER_REGION_NET_UNRESOLVED"
        and issue.object_id == "R1"
        for issue in report.issues
    )


def test_degenerate_region_is_reported_and_not_exported(tmp_path: Path):
    region = CopperRegion(
        "Rbad",
        (Point(0, 0), Point(1, 0), Point(0, 0)),
        "F.Cu",
    )

    path, report = export_kicad_with_report(
        BoardModel(regions=[region]),
        tmp_path / "degenerate_region.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 0
    assert report.skipped_regions == 1
    assert "(zone" not in text
    assert any(
        issue.code == "KICAD_COPPER_REGION_INVALID_GEOMETRY"
        and issue.object_id == "Rbad"
        for issue in report.issues
    )
