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
    refdes_confidence: float = 1.0,
    pin: str | None = None,
    pin_function: str | None = None,
    step_repeat: str | None = None,
) -> PadCandidate:
    pad = PadCandidate(
        pad_id,
        Point(x, 0.0),
        1.0,
        1.0,
        "C",
        "F.Cu",
    )
    if refdes is not None:
        pad.provenance.add_evidence(
            Evidence(
                "gerber_x2_component_refdes",
                refdes,
                refdes_confidence,
            )
        )
    if pin is not None:
        pad.provenance.add_evidence(
            Evidence("gerber_x2_pin_number", pin, 1.0)
        )
    if pin_function is not None:
        pad.provenance.add_evidence(
            Evidence("gerber_x2_pin_function", pin_function, 1.0)
        )
    if step_repeat is not None:
        pad.provenance.add_evidence(
            Evidence("gerber_step_repeat", step_repeat, 1.0)
        )
    return pad


def _signature(components):
    return [
        (
            component.id,
            component.reference,
            tuple(component.pad_ids),
            component.kind,
            component.confidence,
        )
        for component in components
    ]


def test_trusted_x2_refdes_groups_pads_before_geometry():
    board = BoardModel(
        pads=[
            _pad(
                "P1",
                0.0,
                refdes="U1",
                pin="1",
                pin_function="VCC",
            ),
            _pad(
                "P2",
                100.0,
                refdes="U1",
                pin="2",
                pin_function="GND",
            ),
            _pad("P3", 10.0),
            _pad("P4", 11.0),
        ]
    )

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=2.0,
        backend="python",
    )

    source = [
        item
        for item in components
        if item.kind == "gerber_x2_component"
    ]
    assert len(source) == 1
    assert source[0].reference == "U1"
    assert source[0].pad_ids == ["P1", "P2"]
    assert source[0].confidence == 1.0
    assert any(
        "P1=1 (VCC)" in item and "P2=2 (GND)" in item
        for item in source[0].evidence
    )

    geometric = [
        item
        for item in components
        if item.kind == "two_pad_component_candidate"
    ]
    assert len(geometric) == 1
    assert geometric[0].pad_ids == ["P3", "P4"]


def test_lower_confidence_x2_refdes_does_not_become_certain():
    board = BoardModel(
        pads=[
            _pad(
                "P1",
                0.0,
                refdes="U9",
                refdes_confidence=0.6,
            ),
            _pad("P2", 1.0),
        ]
    )

    components = infer_component_hypotheses(board)

    assert len(components) == 1
    assert components[0].reference is None
    assert components[0].pad_ids == ["P1", "P2"]
    assert components[0].confidence < 1.0


def test_conflicting_trusted_x2_refdes_isolated_from_geometry():
    pad = _pad("P1", 0.0, refdes="U1")
    pad.provenance.add_evidence(
        Evidence("gerber_x2_component_refdes", "U2", 1.0)
    )
    board = BoardModel(
        pads=[
            pad,
            _pad("P2", 0.5),
        ]
    )

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=2.0,
        backend="python",
    )

    conflict = [
        item
        for item in components
        if item.kind == "gerber_x2_component_conflict"
    ]
    assert len(conflict) == 1
    assert conflict[0].pad_ids == ["P1"]
    assert conflict[0].reference is None
    assert conflict[0].confidence == 0.0

    unresolved = [
        item
        for item in components
        if item.kind == "unresolved_pad"
    ]
    assert len(unresolved) == 1
    assert unresolved[0].pad_ids == ["P2"]
    assert not any(
        set(item.pad_ids) == {"P1", "P2"}
        for item in components
    )


def test_duplicate_trusted_x2_pin_number_fails_closed_for_component():
    board = BoardModel(
        pads=[
            _pad("P1", 0.0, refdes="U1", pin="1"),
            _pad("P2", 10.0, refdes="U1", pin="1"),
        ]
    )

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=2.0,
        backend="python",
    )

    assert len(components) == 1
    conflict = components[0]
    assert conflict.kind == "gerber_x2_component_conflict"
    assert conflict.reference == "U1"
    assert conflict.pad_ids == ["P1", "P2"]
    assert conflict.confidence == 0.0
    assert any(
        "pin '1' assigned to multiple pads: P1, P2" in item
        for item in conflict.evidence
    )


def test_conflicting_trusted_x2_pin_values_fail_closed_for_component():
    pad = _pad("P1", 0.0, refdes="U1", pin="1")
    pad.provenance.add_evidence(
        Evidence("gerber_x2_pin_number", "2", 1.0)
    )
    board = BoardModel(
        pads=[
            pad,
            _pad("P2", 10.0, refdes="U1", pin="3"),
        ]
    )

    components = infer_component_hypotheses(board, backend="python")

    assert len(components) == 1
    conflict = components[0]
    assert conflict.kind == "gerber_x2_component_conflict"
    assert conflict.reference == "U1"
    assert conflict.pad_ids == ["P1", "P2"]
    assert conflict.confidence == 0.0
    assert any(
        "P1 has conflicting trusted Gerber X2 .P pin numbers: '1', '2'"
        in item
        for item in conflict.evidence
    )


def test_conflicting_trusted_x2_pin_functions_fail_closed_for_component():
    pad = _pad(
        "P1",
        0.0,
        refdes="U1",
        pin="1",
        pin_function="VCC",
    )
    pad.provenance.add_evidence(
        Evidence("gerber_x2_pin_function", "GND", 1.0)
    )
    board = BoardModel(
        pads=[
            pad,
            _pad("P2", 10.0, refdes="U1", pin="2"),
        ]
    )

    components = infer_component_hypotheses(board, backend="python")

    assert len(components) == 1
    conflict = components[0]
    assert conflict.kind == "gerber_x2_component_conflict"
    assert conflict.reference == "U1"
    assert conflict.pad_ids == ["P1", "P2"]
    assert conflict.confidence == 0.0
    assert any(
        "P1 has conflicting trusted Gerber X2 .P pin functions: 'GND', 'VCC'"
        in item
        for item in conflict.evidence
    )


def test_step_repeat_instances_with_same_refdes_stay_separate():
    board = BoardModel(
        pads=[
            _pad(
                "A1",
                0.0,
                refdes="U1",
                pin="1",
                step_repeat="instance=(1,1)/(2,1)",
            ),
            _pad(
                "A2",
                1.0,
                refdes="U1",
                pin="2",
                step_repeat="instance=(1,1)/(2,1)",
            ),
            _pad(
                "B1",
                20.0,
                refdes="U1",
                pin="1",
                step_repeat="instance=(2,1)/(2,1)",
            ),
            _pad(
                "B2",
                21.0,
                refdes="U1",
                pin="2",
                step_repeat="instance=(2,1)/(2,1)",
            ),
        ]
    )

    components = infer_component_hypotheses(
        board,
        max_pair_distance_mm=2.0,
        backend="python",
    )

    source = [
        item
        for item in components
        if item.kind == "gerber_x2_component"
    ]
    assert len(source) == 2
    assert {tuple(item.pad_ids) for item in source} == {
        ("A1", "A2"),
        ("B1", "B2"),
    }
    assert {item.reference for item in source} == {"U1"}
    assert len({item.id for item in source}) == 2


def test_x2_source_inference_has_spatial_bruteforce_parity():
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
