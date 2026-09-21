import pytest

from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.mechanical_features.model import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    ComponentHypothesis,
    DrillHit,
    NetGroup,
    PadCandidate,
    ParseDiagnostic,
    Point,
)
from photonx_eda_pcb.review_queue import build_board_review_queue
from photonx_eda_pcb.validation import ValidationIssue, ValidationReport


def _board() -> BoardModel:
    return BoardModel(
        drills=[
            DrillHit("D1", Point(0, 0), 0.4, "unknown", "T01"),
            DrillHit("D2", Point(1, 0), 0.4, "plated", "T02"),
        ],
        slots=[
            SlotFeature("S1", (0, 0), (1, 0), 0.5, "unknown"),
            SlotFeature("S2", (0, 1), (1, 1), 0.5, "plated"),
        ],
        nets=[
            NetGroup("N1", ["D1"], 0.90),
            NetGroup("N2", ["D2"], 0.80, label="GND"),
        ],
        components=[
            ComponentHypothesis("C1", ["D1"], "TWO_PIN_THT", 0.70, ["geometry"]),
            ComponentHypothesis(
                "C2", ["D2"], "TWO_PIN_THT", 0.60, ["geometry"], reference="R1"
            ),
        ],
        diagnostics=[
            ParseDiagnostic(
                "warning",
                "UNSUPPORTED_HINT",
                "ignored non-geometric hint",
                "top.gbr",
                12,
            )
        ],
    )


def test_board_review_queue_surfaces_explicit_unresolved_state_deterministically():
    first = build_board_review_queue(_board())
    second = build_board_review_queue(_board())

    items = first.open_items()
    targets = {(item.kind, item.target_id) for item in items}

    assert ("drill", "D1") in targets
    assert ("slot", "S1") in targets
    assert ("net", "N1") in targets
    assert ("component", "C1") in targets
    assert ("diagnostic", "top.gbr:12") in targets
    assert ("drill", "D2") not in targets
    assert ("slot", "S2") not in targets
    assert ("net", "N2") not in targets
    assert ("component", "C2") not in targets
    assert [item.id for item in items] == [item.id for item in second.open_items()]

    diagnostic = next(item for item in items if item.kind == "diagnostic")
    assert diagnostic.metadata["confidence_available"] is False


def test_validation_findings_are_included_without_inventing_confidence():
    report = ValidationReport(
        [ValidationIssue("error", "TEST_ERROR", "test issue", ("D1",))]
    )

    queue = build_board_review_queue(_board(), validation=report)
    item = next(item for item in queue.all() if item.kind == "validation")

    assert item.target_id == "D1"
    assert item.metadata["selectable_object_id"] == "D1"
    assert item.metadata["confidence_available"] is False
    assert item.metadata["code"] == "TEST_ERROR"


def test_validation_without_selectable_object_remains_reviewable():
    report = ValidationReport(
        [ValidationIssue("warning", "BOARD_WARNING", "board-level issue")]
    )

    queue = build_board_review_queue(_board(), validation=report)
    item = next(item for item in queue.all() if item.kind == "validation")

    assert item.target_id == "validation:BOARD_WARNING"
    assert item.metadata["selectable_object_id"] is None


def test_confidence_review_thresholds_are_explicit_and_opt_in():
    board = _board()

    default_targets = {
        (item.kind, item.target_id) for item in build_board_review_queue(board).all()
    }
    assert ("net", "N2") not in default_targets
    assert ("component", "C2") not in default_targets

    threshold_targets = {
        (item.kind, item.target_id)
        for item in build_board_review_queue(
            board,
            net_confidence_below=0.85,
            component_confidence_below=0.65,
        ).all()
    }
    assert ("net", "N2") in threshold_targets
    assert ("component", "C2") in threshold_targets


@pytest.mark.parametrize("value", [-0.01, 1.01, float("inf"), float("nan")])
def test_review_thresholds_reject_invalid_values(value):
    with pytest.raises(ValueError):
        build_board_review_queue(_board(), net_confidence_below=value)



def _via_review_board(*, proven=True, conflict=False) -> BoardModel:
    second_net = "N2" if conflict else "N1"
    nets = [NetGroup("N1", [], 1.0, label="GND")]
    if conflict:
        nets.append(NetGroup("N2", [], 1.0, label="VCC"))
    return BoardModel(
        pads=[
            PadCandidate("P_F", Point(0, 0), 1.0, 1.0, "C", "F.Cu", None, "N1"),
            PadCandidate("P_B", Point(0, 0), 1.0, 1.0, "C", "B.Cu", None, second_net),
        ],
        drills=[DrillHit("DV", Point(0, 0), 0.4, "plated")],
        nets=nets,
        metadata={
            "via_spans": [
                {
                    "drill_id": "DV",
                    "from_layer": "F.Cu",
                    "to_layer": "B.Cu",
                    "confidence": 0.9,
                    "proven": proven,
                    "pad_ids": ["P_F", "P_B"],
                    "layer_ids": ["F.Cu", "B.Cu"],
                    "evidence": ["test evidence"],
                }
            ]
        },
    )


def test_canonical_review_queue_skips_exactly_exportable_via_span():
    queue = build_board_review_queue(
        _via_review_board(),
        include_unresolved_clearance=False,
        include_diagnostics=False,
    )

    assert not any(item.kind == "via_span" for item in queue.all())


def test_canonical_review_queue_surfaces_kicad_via_omission_reason():
    queue = build_board_review_queue(
        _via_review_board(conflict=True),
        include_unresolved_clearance=False,
        include_diagnostics=False,
    )

    item = next(item for item in queue.all() if item.kind == "via_span")
    assert item.target_id == "DV"
    assert item.metadata["status"] == "omitted"
    assert item.metadata["export_code"] == "KICAD_PROVEN_VIA_NET_CONFLICT"
    assert item.metadata["selectable_object_id"] == "DV"
    assert item.metadata["confidence_available"] is True


def test_canonical_review_queue_surfaces_unproven_via_span_and_can_disable_it():
    board = _via_review_board(proven=False)

    queue = build_board_review_queue(
        board,
        include_unresolved_clearance=False,
        include_diagnostics=False,
    )
    item = next(item for item in queue.all() if item.kind == "via_span")
    assert item.metadata["status"] == "unproven"
    assert item.confidence == pytest.approx(0.9)

    disabled = build_board_review_queue(
        board,
        include_via_evidence=False,
        include_unresolved_clearance=False,
        include_diagnostics=False,
    )
    assert not any(item.kind == "via_span" for item in disabled.all())



def _route_review_board(*, exportable=False) -> BoardModel:
    if exportable:
        route = RoutedPath(
            "R_EXACT",
            ((0.0, 0.0), (3.0, 0.0)),
            0.6,
            plated="non-plated",
        )
    else:
        route = RoutedPath(
            "R_REVIEW",
            ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0)),
            0.6,
            plated="non-plated",
        )
    return BoardModel(routes=[route])


def test_canonical_review_queue_skips_exactly_exportable_route():
    queue = build_board_review_queue(
        _route_review_board(exportable=True),
        include_unresolved_clearance=False,
        include_diagnostics=False,
    )

    assert not any(item.kind == "route_evidence" for item in queue.all())


def test_canonical_review_queue_surfaces_route_omission_and_can_disable_it():
    board = _route_review_board()

    queue = build_board_review_queue(
        board,
        include_unresolved_clearance=False,
        include_diagnostics=False,
    )
    item = next(item for item in queue.all() if item.kind == "route_evidence")
    assert item.target_id == "R_REVIEW"
    assert item.metadata["status"] == "omitted"
    assert item.metadata["export_code"] == "KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
    assert item.metadata["selectable_object_id"] == "R_REVIEW"
    assert item.metadata["confidence_available"] is False

    disabled = build_board_review_queue(
        board,
        include_route_evidence=False,
        include_unresolved_clearance=False,
        include_diagnostics=False,
    )
    assert not any(item.kind == "route_evidence" for item in disabled.all())
