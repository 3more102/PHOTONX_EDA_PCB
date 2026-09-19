import pytest

from photonx_eda_pcb.checks.ids import check_unique_object_ids
from photonx_eda_pcb.drc.duplicates import check_duplicate_ids
from photonx_eda_pcb.excellon_routing.model import RoutedPath
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import BoardModel, CopperRegion, Point, Track
from photonx_eda_pcb.validation_rules.id_rules import unique_object_ids


@pytest.mark.parametrize(
    ("field", "obj"),
    [
        ("slots", SlotFeature("dup", (0.0, 0.0), (1.0, 0.0), 0.5)),
        ("routes", RoutedPath("dup", ((0.0, 0.0), (1.0, 0.0)), 0.2)),
        (
            "regions",
            CopperRegion(
                "dup",
                (Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)),
                "F.Cu",
            ),
        ),
    ],
)
def test_duplicate_id_checks_include_extended_physical_objects(field, obj):
    board = BoardModel(
        tracks=[Track("dup", Point(0.0, 0.0), Point(1.0, 0.0), 0.2, "F.Cu")],
        **{field: [obj]},
    )

    assert any(
        issue.code == "DUPLICATE_OBJECT_ID" and issue.object_id == "dup"
        for issue in check_unique_object_ids(board)
    )
    assert any(
        issue.code == "DUPLICATE_ID" and issue.object_ids == ("dup",)
        for issue in check_duplicate_ids(board, None)
    )
    assert any(
        issue.code == "DUPLICATE_ID" and issue.object_id == "dup"
        for issue in unique_object_ids(board)
    )


def test_object_index_uses_the_same_complete_physical_object_collection():
    slot = SlotFeature("slot", (0.0, 0.0), (1.0, 0.0), 0.5)
    route = RoutedPath("route", ((0.0, 0.0), (1.0, 0.0)), 0.2)
    region = CopperRegion(
        "region",
        (Point(0.0, 0.0), Point(1.0, 0.0), Point(0.0, 1.0)),
        "F.Cu",
    )
    board = BoardModel(slots=[slot], routes=[route], regions=[region])

    assert board.object_index() == {
        "slot": slot,
        "route": route,
        "region": region,
    }
