from dataclasses import replace

from photonx_eda_pcb.board_statistics import compute_board_stats, validate_stats
from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    OutlineSegment,
    ParseDiagnostic,
    Point,
    Track,
)
from photonx_eda_pcb.reporting import summary
from photonx_eda_pcb.reporting.text import render_text_report


def _board_with_extended_physical_evidence() -> BoardModel:
    return BoardModel(
        tracks=[Track("T", Point(0, 0), Point(3, 4), 0.2, "F.Cu")],
        outline=[
            OutlineSegment("O1", Point(0, 0), Point(10, 0)),
            OutlineSegment("O2", Point(10, 0), Point(10, 5)),
        ],
        slots=[SlotFeature("S", (0, 0), (1, 0), 0.5)],
        routes=[RoutedPath("R", ((0, 0), (0, 3), (4, 3)), 0.5)],
        regions=[
            CopperRegion(
                "C",
                (
                    Point(0, 0),
                    Point(1, 0),
                    Point(1, 1),
                    Point(0, 0),
                ),
                "F.Cu",
            )
        ],
        diagnostics=[
            ParseDiagnostic("warning", "TEST", "synthetic diagnostic", "board.gbr")
        ],
    )


def test_legacy_board_statistics_cover_current_physical_model():
    board = _board_with_extended_physical_evidence()

    stats = compute_board_stats(board)

    assert stats.tracks == 1
    assert stats.slots == 1
    assert stats.routes == 1
    assert stats.regions == 1
    assert stats.diagnostics == 1
    assert stats.total_track_length_mm == 5.0
    assert stats.route_length_mm == 7.0
    assert stats.outline_length_mm == 15.0
    assert stats.board_width_mm == 10.0
    assert stats.board_height_mm == 5.0
    assert validate_stats(stats) == []


def test_extended_statistics_validation_covers_new_counts_and_lengths():
    stats = compute_board_stats(_board_with_extended_physical_evidence())
    invalid = replace(stats, routes=-1, route_length_mm=-1.0)

    issues = validate_stats(invalid)

    assert "STATS_NEGATIVE_ROUTES" in issues
    assert "STATS_NEGATIVE_ROUTE_LENGTH" in issues


def test_reporting_surfaces_routes_and_regions_consistently():
    board = _board_with_extended_physical_evidence()

    legacy_summary = summary(board)
    text = render_text_report(board)

    assert legacy_summary["routes"] == 1
    assert legacy_summary["regions"] == 1
    assert "routes=1" in text
    assert "regions=1" in text
