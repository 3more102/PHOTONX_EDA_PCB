from photonx_eda_pcb.models import (
    BoardModel,
    DrillHit,
    NetGroup,
    PadCandidate,
    Point,
)
from photonx_eda_pcb.via_review import (
    build_via_review_descriptors,
    via_review_descriptor,
    via_review_summary,
)


def _span(
    drill_id,
    *,
    from_layer,
    to_layer,
    pad_ids,
    proven=True,
    confidence=1.0,
    layer_ids=(),
):
    return {
        "drill_id": drill_id,
        "from_layer": from_layer,
        "to_layer": to_layer,
        "confidence": confidence,
        "proven": proven,
        "pad_ids": list(pad_ids),
        "layer_ids": list(layer_ids),
        "evidence": ["test evidence"],
    }


def _board():
    return BoardModel(
        pads=[
            PadCandidate(
                "P1",
                Point(0, 0),
                0.8,
                0.8,
                "C",
                "F.Cu",
                net_id="N1",
            ),
            PadCandidate(
                "P1I",
                Point(0, 0),
                0.8,
                0.8,
                "C",
                "In1.Cu",
                net_id="N1",
            ),
            PadCandidate(
                "P2",
                Point(0, 0),
                0.8,
                0.8,
                "C",
                "B.Cu",
                net_id="N1",
            ),
            PadCandidate(
                "P3",
                Point(2, 0),
                0.8,
                0.8,
                "C",
                "F.Cu",
                net_id="N1",
            ),
            PadCandidate(
                "P4",
                Point(2, 0),
                0.8,
                0.8,
                "C",
                "In1.Cu",
                net_id="N1",
            ),
        ],
        drills=[
            DrillHit("D1", Point(0, 0), 0.4, "plated"),
            DrillHit("D2", Point(2, 0), 0.4, "plated"),
            DrillHit("D3", Point(4, 0), 0.4, "unknown"),
        ],
        nets=[
            NetGroup(
                "N1",
                ["P1", "P1I", "P2", "P3", "P4"],
                1.0,
                "SIG",
            )
        ],
        metadata={
            "via_spans": [
                _span(
                    "D1",
                    from_layer="F.Cu",
                    to_layer="B.Cu",
                    pad_ids=("P1", "P1I", "P2"),
                    layer_ids=("F.Cu", "In1.Cu", "B.Cu"),
                ),
                _span(
                    "D2",
                    from_layer="F.Cu",
                    to_layer="In1.Cu",
                    pad_ids=("P3", "P4"),
                    layer_ids=("F.Cu", "In1.Cu"),
                ),
                _span(
                    "D3",
                    from_layer=None,
                    to_layer=None,
                    pad_ids=(),
                    proven=False,
                    confidence=0.25,
                ),
            ]
        },
    )


def test_via_review_classifies_exportable_omitted_and_unproven():
    rows = build_via_review_descriptors(_board())

    assert [row.drill_id for row in rows] == ["D1", "D2", "D3"]
    assert [row.status for row in rows] == [
        "exportable",
        "omitted",
        "unproven",
    ]

    assert rows[0].net_id == "N1"
    assert rows[0].export_code is None
    assert rows[1].export_code == "KICAD_PROVEN_VIA_TYPE_UNPROVEN"
    assert rows[2].confidence == 0.25


def test_via_review_descriptor_preserves_source_evidence():
    row = via_review_descriptor(_board(), "D1")

    assert row is not None
    assert row.plating == "plated"
    assert row.from_layer == "F.Cu"
    assert row.to_layer == "B.Cu"
    assert row.pad_ids == ("P1", "P1I", "P2")
    assert row.layer_ids == ("F.Cu", "In1.Cu", "B.Cu")
    assert row.evidence == ("test evidence",)


def test_via_review_summary_is_deterministic():
    assert via_review_summary(_board()) == {
        "exportable": 1,
        "omitted": 1,
        "unproven": 1,
        "invalid": 0,
    }
