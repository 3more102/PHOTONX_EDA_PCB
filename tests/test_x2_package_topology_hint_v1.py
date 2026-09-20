from photonx_eda_pcb.inference.components import infer_component_hypotheses
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point
from photonx_eda_pcb.provenance import Evidence


def _x2_pad(pad_id, x, y, refdes, pin, drill=None):
    pad = PadCandidate(
        pad_id,
        Point(x, y),
        1.0,
        0.6,
        "R",
        "F.Cu",
        drill,
    )
    pad.provenance.add_evidence(
        Evidence("gerber_x2_component_refdes", refdes, 1.0)
    )
    pad.provenance.add_evidence(
        Evidence("gerber_x2_pin_number", str(pin), 1.0)
    )
    return pad


def test_x2_identity_gains_machine_readable_soic8_package_hint():
    pads = []
    pin = 1
    for y in (-2.5, 2.5):
        for x in (-1.905, -0.635, 0.635, 1.905):
            pads.append(_x2_pad(f"P{pin}", x, y, "U1", pin))
            pin += 1

    components = infer_component_hypotheses(BoardModel(pads=pads), backend="python")

    assert len(components) == 1
    component = components[0]
    assert component.kind == "gerber_x2_component"
    assert component.reference == "U1"
    assert component.confidence == 1.0
    assert component.package_hint == "SOIC8_LIKE"
    assert any(
        "pad-topology package hint: SOIC8_LIKE" in item
        for item in component.evidence
    )


def test_x2_identity_is_preserved_when_package_geometry_is_unproven():
    board = BoardModel(
        pads=[
            _x2_pad("P1", 0.0, 0.0, "J1", 1),
            _x2_pad("P2", 100.0, 0.0, "J1", 2),
        ]
    )

    components = infer_component_hypotheses(board, backend="python")

    assert len(components) == 1
    component = components[0]
    assert component.reference == "J1"
    assert component.confidence == 1.0
    assert component.package_hint is None
    assert any(
        "package hint unresolved" in item
        for item in component.evidence
    )


def test_geometric_two_pad_candidate_gets_only_supported_package_hint():
    board = BoardModel(
        pads=[
            PadCandidate("A", Point(0.0, 0.0), 1.0, 0.6, "R", "F.Cu"),
            PadCandidate("B", Point(2.0, 0.0), 1.0, 0.6, "R", "F.Cu"),
        ]
    )

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=4.0,
        backend="python",
    )

    assert len(components) == 1
    component = components[0]
    assert component.kind == "two_pad_component_candidate"
    assert component.package_hint == "TWO_PAD_SMD"
    assert component.confidence < 1.0
