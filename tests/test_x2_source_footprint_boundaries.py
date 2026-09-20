from photonx_eda_pcb.footprints.infer import infer_footprints
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point
from photonx_eda_pcb.provenance import Evidence


def _pad(
    pad_id,
    x,
    *,
    refdes=None,
    refdes_confidence=1.0,
    pin=None,
    pin_function=None,
    step_repeat=None,
):
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


def test_trusted_x2_boundary_wins_before_geometric_clustering():
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
                20.0,
                refdes="U1",
                pin="2",
                pin_function="GND",
            ),
            _pad("P3", 0.4),
        ]
    )

    candidates = infer_footprints(
        board,
        max_gap_mm=1.0,
        backend="python",
    )

    source = next(
        item
        for item in candidates
        if item.boundary_source == "gerber_x2_component_refdes"
    )
    assert source.reference == "U1"
    assert source.pad_ids == ["P1", "P2"]
    assert source.boundary_confidence == 1.0
    assert any(
        "P1=1 (VCC)" in item and "P2=2 (GND)" in item
        for item in source.evidence
    )

    geometric = next(
        item
        for item in candidates
        if item.boundary_source == "geometric_proximity"
    )
    assert geometric.pad_ids == ["P3"]
    assert geometric.reference is None
    assert geometric.boundary_confidence == 0.0
    assert not any(
        set(item.pad_ids) == {"P1", "P3"}
        for item in candidates
    )


def test_conflicting_trusted_refdes_is_fail_closed_and_withheld():
    pad = _pad("P1", 0.0, refdes="U1")
    pad.provenance.add_evidence(
        Evidence("gerber_x2_component_refdes", "U2", 1.0)
    )
    board = BoardModel(
        pads=[
            pad,
            _pad("P2", 0.2),
        ]
    )

    candidates = infer_footprints(
        board,
        max_gap_mm=1.0,
        backend="python",
    )

    conflict = next(
        item
        for item in candidates
        if item.boundary_source == "gerber_x2_refdes_conflict"
    )
    assert conflict.pad_ids == ["P1"]
    assert conflict.signature is None
    assert conflict.confidence == 0.0
    assert conflict.boundary_confidence == 0.0
    assert any("withheld from geometric" in item for item in conflict.evidence)

    geometric = next(
        item
        for item in candidates
        if item.boundary_source == "geometric_proximity"
    )
    assert geometric.pad_ids == ["P2"]
    assert not any(
        set(item.pad_ids) == {"P1", "P2"}
        for item in candidates
    )


def test_lower_confidence_x2_identity_stays_geometric():
    board = BoardModel(
        pads=[
            _pad(
                "P1",
                0.0,
                refdes="U9",
                refdes_confidence=0.6,
            ),
            _pad("P2", 0.5),
        ]
    )

    candidates = infer_footprints(
        board,
        max_gap_mm=1.0,
        backend="python",
    )

    assert len(candidates) == 1
    assert candidates[0].pad_ids == ["P1", "P2"]
    assert candidates[0].reference is None
    assert candidates[0].boundary_source == "geometric_proximity"
    assert candidates[0].boundary_confidence == 0.0


def test_step_repeat_instances_with_same_refdes_stay_separate():
    board = BoardModel(
        pads=[
            _pad(
                "A1",
                0.0,
                refdes="U1",
                step_repeat="instance=(1,1)/(2,1)",
            ),
            _pad(
                "A2",
                0.5,
                refdes="U1",
                step_repeat="instance=(1,1)/(2,1)",
            ),
            _pad(
                "B1",
                10.0,
                refdes="U1",
                step_repeat="instance=(2,1)/(2,1)",
            ),
            _pad(
                "B2",
                10.5,
                refdes="U1",
                step_repeat="instance=(2,1)/(2,1)",
            ),
        ]
    )

    candidates = infer_footprints(board, backend="python")
    source = [
        item
        for item in candidates
        if item.boundary_source == "gerber_x2_component_refdes"
    ]

    assert len(source) == 2
    assert {tuple(item.pad_ids) for item in source} == {
        ("A1", "A2"),
        ("B1", "B2"),
    }
    assert {item.reference for item in source} == {"U1"}
    assert len({item.id for item in source}) == 2


def test_footprint_ids_are_stable_under_pad_input_order():
    pads = [
        _pad("P1", 0.0),
        _pad("P2", 0.5),
        _pad("P3", 10.0, refdes="R1"),
        _pad("P4", 11.0, refdes="R1"),
    ]

    first = infer_footprints(
        BoardModel(pads=list(pads)),
        max_gap_mm=1.0,
        backend="python",
    )
    second = infer_footprints(
        BoardModel(pads=list(reversed(pads))),
        max_gap_mm=1.0,
        backend="python",
    )

    assert {
        (item.id, tuple(item.pad_ids), item.reference, item.boundary_source)
        for item in first
    } == {
        (item.id, tuple(item.pad_ids), item.reference, item.boundary_source)
        for item in second
    }
