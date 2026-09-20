from photonx_eda_pcb.inference.components import (
    infer_component_hypotheses,
    infer_component_hypotheses_bruteforce,
)
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point
from photonx_eda_pcb.provenance import Evidence


def _pad(
    pad_id: str,
    x: float,
    *,
    refdes: str | None = None,
    pin: str | None = None,
):
    pad = PadCandidate(pad_id, Point(x, 0.0), 1.0, 1.0, "C", "F.Cu")
    if refdes is not None:
        pad.provenance.add_evidence(
            Evidence("gerber_x2_component_refdes", refdes, 1.0)
        )
    if pin is not None:
        pad.provenance.add_evidence(
            Evidence("gerber_x2_pin_number", pin, 1.0)
        )
    return pad


def _signature(items):
    return [
        (item.reference, tuple(item.pad_ids), item.kind, item.confidence)
        for item in items
    ]


def test_x2_refdes_groups_source_proven_pads_before_geometry():
    board = BoardModel(
        pads=[
            _pad("P1", 0.0, refdes="U1", pin="1"),
            _pad("P2", 20.0, refdes="U1", pin="2"),
            _pad("P3", 40.0),
            _pad("P4", 41.0),
        ]
    )

    components = infer_component_hypotheses(board)

    source = [item for item in components if item.reference == "U1"]
    assert len(source) == 1
    assert source[0].pad_ids == ["P1", "P2"]
    assert source[0].kind == "gerber_x2_component"
    assert source[0].confidence == 1.0
    assert any(
        "P1=1" in item and "P2=2" in item
        for item in source[0].evidence
    )

    geometric = [item for item in components if item.reference is None]
    assert len(geometric) == 1
    assert geometric[0].pad_ids == ["P3", "P4"]


def test_conflicting_x2_refdes_on_one_pad_is_not_promoted():
    p1 = _pad("P1", 0.0, refdes="U1")
    p1.provenance.add_evidence(
        Evidence("gerber_x2_component_refdes", "U2", 1.0)
    )
    board = BoardModel(pads=[p1, _pad("P2", 1.0)])

    components = infer_component_hypotheses(board)

    assert len(components) == 1
    assert components[0].reference is None
    assert components[0].pad_ids == ["P1", "P2"]


def test_x2_component_seed_has_spatial_and_bruteforce_parity():
    spatial_pads = [
        _pad("P1", 0.0, refdes="J1", pin="1"),
        _pad("P2", 50.0, refdes="J1", pin="2"),
        _pad("P3", 10.0),
        _pad("P4", 11.0),
    ]
    brute_pads = [
        _pad("P1", 0.0, refdes="J1", pin="1"),
        _pad("P2", 50.0, refdes="J1", pin="2"),
        _pad("P3", 10.0),
        _pad("P4", 11.0),
    ]
    spatial = infer_component_hypotheses(BoardModel(pads=spatial_pads))
    brute = infer_component_hypotheses_bruteforce(BoardModel(pads=brute_pads))

    assert _signature(spatial) == _signature(brute)


def test_lower_confidence_refdes_evidence_is_not_promoted_to_certainty():
    p1 = _pad("P1", 0.0)
    p1.provenance.add_evidence(
        Evidence("gerber_x2_component_refdes", "U9", 0.6)
    )
    board = BoardModel(pads=[p1, _pad("P2", 1.0)])

    components = infer_component_hypotheses(board)

    assert len(components) == 1
    assert components[0].reference is None
    assert components[0].confidence < 1.0
