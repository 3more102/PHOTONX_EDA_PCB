from photonx_eda_pcb.gui.via_review import build_via_evidence_rows
from photonx_eda_pcb.models import BoardModel, DrillHit, NetGroup, PadCandidate, Point


def _pad(pad_id, layer, *, net_id="N1", size=1.0):
    return PadCandidate(
        pad_id,
        Point(0, 0),
        size,
        size,
        "C",
        layer,
        None,
        net_id,
    )


def _span(*pad_ids, proven=True, confidence=0.95):
    return {
        "drill_id": "D1",
        "from_layer": "F.Cu",
        "to_layer": "B.Cu",
        "confidence": confidence,
        "proven": proven,
        "pad_ids": list(pad_ids),
        "layer_ids": ["F.Cu", "B.Cu"],
        "evidence": ["test evidence"],
    }


def _board(span, *, pads=None, plating="plated", nets=None):
    return BoardModel(
        pads=pads
        or [
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, plating)],
        nets=nets or [NetGroup("N1", [], 1.0, "GND")],
        metadata={"via_spans": [span]},
    )


def test_via_evidence_marks_exact_proven_span_exportable():
    rows = build_via_evidence_rows(_board(_span("P_F", "P_B")))

    assert len(rows) == 1
    row = rows[0]
    assert row["status"] == "exportable"
    assert row["drill_id"] == "D1"
    assert row["plating"] == "plated"
    assert row["layers"] == "F.Cu -> B.Cu"
    assert row["net_id"] == "N1"
    assert row["net"] == "N1"
    assert row["confidence"] == 0.95
    assert row["export_code"] is None


def test_via_evidence_surfaces_exact_kicad_omission_reason():
    board = _board(
        _span("P_F", "P_B"),
        pads=[
            _pad("P_F", "F.Cu", net_id="N1"),
            _pad("P_B", "B.Cu", net_id="N2"),
        ],
        nets=[
            NetGroup("N1", [], 1.0, "GND"),
            NetGroup("N2", [], 1.0, "VCC"),
        ],
    )

    row = build_via_evidence_rows(board)[0]

    assert row["status"] == "omitted"
    assert row["net"] == "<conflict>"
    assert row["net_id"] is None
    assert row["export_code"] == "KICAD_PROVEN_VIA_NET_CONFLICT"
    assert "do not agree on one reconstructed net" in row["reason"]


def test_via_evidence_keeps_unproven_span_explicit():
    row = build_via_evidence_rows(
        _board(
            _span("P_F", "P_B", proven=False, confidence=0.7),
            plating="unknown",
        )
    )[0]

    assert row["status"] == "unproven"
    assert row["plating"] == "unknown"
    assert row["net_id"] == "N1"
    assert row["confidence"] == 0.7
    assert "does not prove a vertical electrical via" in row["reason"]


def test_via_evidence_fails_closed_on_duplicate_span_identity():
    board = _board(_span("P_F", "P_B"))
    board.metadata["via_spans"] = [
        _span("P_F", "P_B"),
        _span("P_F", "P_B"),
    ]

    rows = build_via_evidence_rows(board)

    assert [row["status"] for row in rows] == ["invalid", "invalid"]
    assert all(
        row["reason"] == "duplicate via-span drill ID in reconstruction metadata"
        for row in rows
    )


def test_via_evidence_reports_invalid_metadata_container():
    board = BoardModel(metadata={"via_spans": "not-a-list"})

    rows = build_via_evidence_rows(board)

    assert rows == [
        {
            "id": "via-span:metadata",
            "drill_id": "via_spans",
            "status": "invalid",
            "plating": "—",
            "layers": "—",
            "net": "—",
            "net_id": None,
            "confidence": None,
            "pad_ids": (),
            "reason": "via_spans metadata must be a list or tuple",
            "export_code": None,
        }
    ]
