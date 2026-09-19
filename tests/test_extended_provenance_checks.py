import pytest

from photonx_eda_pcb.checks.provenance import check_provenance
from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import BoardModel, CopperRegion, Point
from photonx_eda_pcb.provenance import Provenance, SourceRef
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
def test_missing_source_checks_cover_extended_physical_objects(field, obj):
    board = BoardModel(**{field: [obj]})

    check_issues = check_provenance(board)
    rule_issues = source_references_present(board)

    assert any(
        issue.code == "PROVENANCE_SOURCE_MISSING" and issue.object_id == obj.id
        for issue in check_issues
    )
    assert any(
        issue.code == "SOURCE_REF_MISSING" and issue.object_id == obj.id
        for issue in rule_issues
    )


@pytest.mark.parametrize(
    ("field", "obj"),
    [
        (
            "slots",
            SlotFeature(
                "slot",
                (0.0, 0.0),
                (1.0, 0.0),
                0.5,
                provenance=Provenance([SourceRef("board.drl", 1, "G85")], []),
            ),
        ),
        (
            "routes",
            RoutedPath(
                "route",
                ((0.0, 0.0), (1.0, 0.0)),
                0.2,
                provenance=Provenance([SourceRef("board.drl", 2, "G01")], []),
            ),
        ),
        (
            "regions",
            CopperRegion(
                "region",
                (Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)),
                "F.Cu",
                provenance=Provenance([SourceRef("board.gbr", 3, "G36")], []),
            ),
        ),
    ],
)
def test_present_sources_are_not_flagged_for_extended_physical_objects(field, obj):
    board = BoardModel(**{field: [obj]})

    assert not check_provenance(board)
    assert not source_references_present(board)
