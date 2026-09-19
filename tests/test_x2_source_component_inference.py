from photonx_eda_pcb.inference.components import (
    infer_component_hypotheses,
    infer_component_hypotheses_bruteforce,
)
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point
from photonx_eda_pcb.provenance import Evidence, Provenance


def _pad(
    pad_id: str,
    x: float,
    *,
    refdes: str | None = None,
    pin: str | None = None,
    step_repeat: str | None = None,
) -> PadCandidate:
    provenance = Provenance()
    if refdes is not None:
        provenance.add_evidence(
            Evidence("gerber_x2_component_refdes", refdes, 1.0)
        )
    if pin is not None:
        provenance.add_evidence(
            Evidence("gerber_x2_pin_number", pin, 1.0)
        )
    if step_repeat is not None:
        provenance.add_evidence(
            Evidence("gerber_step_repeat", step_repeat, 1.0)
        )
    return PadCandidate(
        pad_id,
        Point(x, 0.0),
        1.0,
        1.0,
        "C",
        "F.Cu",
        provenance=provenance,
    )


def _signature(components):
    return sorted(
        (
            component.kind,
            component.reference,
            tuple(component.pad_ids),
            component.confidence,
        )
        for component in components
    )


def test_source_refdes_groups_pads_before_distance_pairing():
    board = BoardModel(
        pads=[
            _pad("P1", 0.0, refdes="U1", pin="1"),
            _pad("P2", 100.0, refdes="U1", pin="2"),
            _pad("P3", 10.0),
            _pad("P4", 11.0),
        ]
    )

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=2.0,
        backend="python",
    )

    source = [c for c in components if c.kind == "gerber_x2_component"]
    geometry = [c for c in components if c.kind == "two_pad_component_candidate"]

    assert len(source) == 1
    assert source[0].reference == "U1"
    assert source[0].pad_ids == ["P1", "P2"]
    assert source[0].confidence == 1.0
    assert len(geometry) == 1
    assert geometry[0].pad_ids == ["P3", "P4"]


def test_conflicting_source_refdes_is_not_reassigned_by_geometry():
    pad = _pad("P1", 0.0, refdes="U1", pin="1")
    pad.provenance.add_evidence(
        Evidence("gerber_x2_component_refdes", "U2", 1.0)
    )
    board = BoardModel(pads=[pad, _pad("P2", 0.5)])

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=2.0,
        backend="python",
    )

    conflict = [c for c in components if c.kind == "gerber_x2_component_conflict"]
    assert len(conflict) == 1
    assert conflict[0].pad_ids == ["P1"]
    assert conflict[0].reference is None
    assert conflict[0].confidence == 0.0

    unresolved = [c for c in components if c.kind == "unresolved_pad"]
    assert len(unresolved) == 1
    assert unresolved[0].pad_ids == ["P2"]
    assert not any(
        set(c.pad_ids) == {"P1", "P2"}
        for c in components
    )


def test_step_repeat_instance_keeps_repeated_refdes_groups_separate():
    board = BoardModel(
        pads=[
            _pad("A1", 0.0, refdes="U1", pin="1", step_repeat="instance=(1,1)/(2,1)"),
            _pad("A2", 1.0, refdes="U1", pin="2", step_repeat="instance=(1,1)/(2,1)"),
            _pad("B1", 20.0, refdes="U1", pin="1", step_repeat="instance=(2,1)/(2,1)"),
            _pad("B2", 21.0, refdes="U1", pin="2", step_repeat="instance=(2,1)/(2,1)"),
        ]
    )

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=2.0,
        backend="python",
    )

    source = [c for c in components if c.kind == "gerber_x2_component"]
    assert len(source) == 2
    assert {tuple(c.pad_ids) for c in source} == {
        ("A1", "A2"),
        ("B1", "B2"),
    }
    assert {c.reference for c in source} == {"U1"}


def test_source_evidence_has_spatial_bruteforce_parity():
    def make_board():
        return BoardModel(
            pads=[
                _pad("P1", 0.0, refdes="R1", pin="1"),
                _pad("P2", 8.0, refdes="R1", pin="2"),
                _pad("P3", 20.0),
                _pad("P4", 21.0),
                _pad("P5", 40.0),
            ]
        )

    spatial = infer_component_hypotheses(
        make_board(),
        max_pair_distance_mm=2.0,
        backend="python",
    )
    brute = infer_component_hypotheses_bruteforce(
        make_board(),
        max_pair_distance_mm=2.0,
    )

    assert _signature(spatial) == _signature(brute)
