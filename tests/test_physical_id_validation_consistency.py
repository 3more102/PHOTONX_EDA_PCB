from photonx_eda_pcb.checks.ids import check_unique_object_ids
from photonx_eda_pcb.drc.duplicates import check_duplicate_ids
from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import BoardModel, CopperRegion, Point, Track
from photonx_eda_pcb.validation_rules.id_rules import unique_object_ids


def _track(object_id: str) -> Track:
    return Track(object_id, Point(0, 0), Point(1, 0), 0.2, "F.Cu")


def _region(object_id: str) -> CopperRegion:
    points = (
        Point(0, 0),
        Point(1, 0),
        Point(0, 1),
        Point(0, 0),
    )
    return CopperRegion(object_id, points, "F.Cu")


def test_extended_physical_objects_participate_in_duplicate_id_checks():
    cases = (
        ("slots", SlotFeature("shared", (0, 0), (1, 0), 0.5)),
        ("routes", RoutedPath("shared", ((0, 0), (1, 0)), 0.5)),
        ("regions", _region("shared")),
    )

    for field_name, extended_object in cases:
        board = BoardModel(tracks=[_track("shared")])
        getattr(board, field_name).append(extended_object)

        check_codes = {issue.code for issue in check_unique_object_ids(board)}
        rule_codes = {issue.code for issue in unique_object_ids(board)}
        drc_codes = {issue.code for issue in check_duplicate_ids(board, None)}

        assert "DUPLICATE_OBJECT_ID" in check_codes
        assert "DUPLICATE_ID" in rule_codes
        assert "DUPLICATE_ID" in drc_codes
