import pytest

from photonx_eda_pcb.analysis.provenance_metrics import evidence_count, source_coverage
from photonx_eda_pcb.checks.provenance import check_provenance
from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import BoardModel, CopperRegion, Point
from photonx_eda_pcb.provenance import Evidence, Provenance, SourceRef
from photonx_eda_pcb.validation_rules.provenance_rules import source_references_present


@pytest.mark.parametrize(
    ("field", "obj"),
    [
        ("slots", SlotFeature("slot", (0.0, 0.0), (1.0, 0.0), 0.5)),
        ("routes", RoutedPath("route", ((0.0, 0.0), (1.0, 0.0)), 0.2)),
        (
            "regions",
            CopperRegion(
                "region",
                (Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)),
                "F.Cu",
            ),
        ),
    ],
)
def test_provenance_checks_include_extended_physical_objects(field, obj):
    board = BoardModel(**{field: [obj]})

    assert any(
        issue.code == "PROVENANCE_SOURCE_MISSING" and issue.object_id == obj.id
        for issue in check_provenance(board)
    )
    assert any(
        issue.code == "SOURCE_REF_MISSING" and issue.object_id == obj.id
        for issue in source_references_present(board)
    )
    assert source_coverage(board) == 0.0


def test_provenance_metrics_count_routes_and_regions():
    provenance = Provenance(
        sources=[SourceRef("board.gbr", 1, "source")],
        evidence=[Evidence("parser", "parsed", 1.0)],
    )
    route = RoutedPath(
        "route",
        ((0.0, 0.0), (1.0, 0.0)),
        0.2,
        provenance=provenance,
    )
    region = CopperRegion(
        "region",
        (Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)),
        "F.Cu",
        provenance=provenance,
    )
    board = BoardModel(routes=[route], regions=[region])

    assert source_coverage(board) == 1.0
    assert evidence_count(board) == 2
