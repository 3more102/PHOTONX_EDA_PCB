from photonx_eda_pcb.gui.state import ViewState
from photonx_eda_pcb.models import (
    BoardModel,
    NetGroup,
    OutlineSegment,
    PadCandidate,
    Point,
    Track,
)
from photonx_eda_pcb.provenance import Evidence, Provenance, SourceRef


def make_board() -> BoardModel:
    provenance = Provenance(
        sources=[SourceRef("top.gtl", 12, "X0Y0D03*")],
        evidence=[
            Evidence(
                "gerber_flash",
                "pad flash",
                0.92,
                SourceRef("top.gtl", 12, "X0Y0D03*"),
            )
        ],
    )
    return BoardModel(
        tracks=[
            Track(
                "T0",
                Point(0, 0),
                Point(5, 0),
                0.2,
                "F.Cu",
            )
        ],
        pads=[
            PadCandidate(
                "P0",
                Point(0, 0),
                1.0,
                1.0,
                "C",
                "F.Cu",
                net_id="N0",
                provenance=provenance,
            )
        ],
        outline=[
            OutlineSegment(
                "O0",
                Point(-1, -1),
                Point(6, -1),
            )
        ],
        nets=[
            NetGroup(
                "N0",
                ["T0", "P0"],
                0.87,
                label="+5V",
            )
        ],
    )


def test_selection_auto_highlights_direct_object_net():
    state = ViewState(make_board())

    assert state.select("P0") == "P0"
    assert state.selected_id == "P0"
    assert state.highlighted_net_id == "N0"


def test_selection_resolves_net_from_membership_when_object_has_no_net_id():
    state = ViewState(make_board())

    assert state.net_for_object("T0").id == "N0"
    state.select("T0")

    assert state.highlighted_net_id == "N0"


def test_non_net_or_unknown_selection_clears_highlight():
    state = ViewState(make_board(), highlighted_net_id="N0")

    state.select("O0")
    assert state.selected_id == "O0"
    assert state.highlighted_net_id is None

    state.select("missing")
    assert state.selected_id is None
    assert state.highlighted_net_id is None


def test_highlight_net_rejects_unknown_ids():
    state = ViewState(make_board())

    assert state.highlight_net("N0") == "N0"
    assert state.highlight_net("missing") is None


def test_inspection_payload_includes_net_and_evidence_summary():
    state = ViewState(make_board())

    payload = state.inspection_payload("P0")

    assert payload["object_type"] == "PadCandidate"
    assert payload["resolved_net"] == {
        "id": "N0",
        "label": "+5V",
        "confidence": 0.87,
        "member_count": 2,
    }
    assert payload["evidence_summary"] == {
        "source_count": 1,
        "evidence_count": 1,
        "max_confidence": 0.92,
    }


def test_inspection_payload_is_explicit_for_missing_object():
    state = ViewState(make_board())

    assert state.inspection_payload("missing") == {
        "id": "missing",
        "status": "not found",
        "resolved_net": None,
    }
