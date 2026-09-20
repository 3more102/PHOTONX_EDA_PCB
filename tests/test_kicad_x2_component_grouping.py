from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import (
    BoardModel,
    ComponentHypothesis,
    NetGroup,
    PadCandidate,
    Point,
)
from photonx_eda_pcb.provenance import Evidence
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


def _x2_pad(pad_id, x, pin, net_id, *, function=None):
    pad = PadCandidate(
        pad_id,
        Point(x, 20.0),
        1.2,
        0.8,
        "R",
        "F.Cu",
        None,
        net_id,
    )
    pad.provenance.add_evidence(
        Evidence("gerber_x2_component_refdes", "U1", 1.0)
    )
    pad.provenance.add_evidence(
        Evidence("gerber_x2_pin_number", pin, 1.0)
    )
    if function is not None:
        pad.provenance.add_evidence(
            Evidence("gerber_x2_pin_function", function, 1.0)
        )
    return pad


def _board(pin2="2"):
    p1 = _x2_pad("P1", 10.0, "1", "N1", function="VCC")
    p2 = _x2_pad("P2", 12.5, pin2, "N2", function="GND")
    component = ComponentHypothesis(
        "CMP_U1",
        ["P1", "P2"],
        "gerber_x2_component",
        1.0,
        ["source-proven Gerber X2 .P"],
        reference="U1",
        source_pin_map={"P1": "1", "P2": pin2},
        source_pin_functions={"P1": "VCC", "P2": "GND"},
    )
    return BoardModel(
        pads=[p1, p2],
        nets=[
            NetGroup("N1", ["P1"], 1.0, "VCC"),
            NetGroup("N2", ["P2"], 1.0, "GND"),
        ],
        components=[component],
    )


def test_source_proven_x2_component_exports_as_one_multi_pad_footprint(tmp_path):
    board = _board()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert text.count('(footprint "PHOTONX:RecoveredX2Component"') == 1
    assert '(footprint "PHOTONX:RecoveredPad"' not in text
    assert '(property "Reference" "U1"' in text
    assert '(pad "1" smd rect' in text
    assert '(pad "2" smd rect' in text
    assert report.exported_pad_ids == ["P1", "P2"]
    assert not any(
        issue.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
        for issue in report.issues
    )

    readback = read_kicad_board_text(text)
    footprint = next(
        item
        for item in readback["footprints"]
        if item["name"] == "PHOTONX:RecoveredX2Component"
    )
    assert footprint["reference"] == "U1"
    assert [pad["number"] for pad in footprint["pads"]] == ["1", "2"]

    audit = compare_kicad_connectivity(board, readback, report)
    assert audit["pads"]["equal"] is True
    assert audit["foreign_footprints"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_equivalent"] is True


def test_x2_pin_number_drift_is_detected_by_roundtrip_audit(tmp_path):
    board = _board()
    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8").replace(
        '(pad "2" smd rect',
        '(pad "9" smd rect',
        1,
    )

    audit = compare_kicad_connectivity(
        board,
        read_kicad_board_text(text),
        report,
    )

    assert audit["pads"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_duplicate_trusted_pin_numbers_fail_closed_to_independent_pads(tmp_path):
    board = _board(pin2="1")
    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-conflict.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredX2Component" not in text
    assert text.count('(footprint "PHOTONX:RecoveredPad"') == 2
    assert report.exported_pad_ids == ["P1", "P2"]
    assert any(
        issue.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
        and issue.object_id == "CMP_U1"
        for issue in report.issues
    )

    audit = compare_kicad_connectivity(
        board,
        read_kicad_board_text(text),
        report,
    )
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True



def test_incomplete_structured_pin_map_fails_closed_to_independent_pads(tmp_path):
    board = _board()
    board.components[0].source_pin_map = {"P1": "1"}
    board.components[0].source_pin_functions = {"P1": "VCC"}

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-incomplete-pin-map.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredX2Component" not in text
    assert text.count('(footprint "PHOTONX:RecoveredPad"') == 2
    issue = next(
        item
        for item in report.issues
        if item.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
    )
    assert "source pin map is incomplete for pads: P2" in issue.message


def test_structured_pin_map_is_the_exported_pin_identity(tmp_path):
    board = _board()
    board.components[0].source_pin_map = {"P1": "A1", "P2": "B2"}

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-structured-pin-map.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '(pad "A1" smd rect' in text
    assert '(pad "B2" smd rect' in text
    assert not any(
        item.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
        for item in report.issues
    )


def test_bottom_side_x2_group_uses_inverse_kicad_footprint_flip(tmp_path):
    p1 = PadCandidate(
        "BP1",
        Point(10.0, 20.0),
        1.2,
        0.8,
        "R",
        "B.Cu",
        None,
        "N1",
    )
    p2 = PadCandidate(
        "BP2",
        Point(12.5, 21.5),
        1.2,
        0.8,
        "R",
        "B.Cu",
        None,
        "N2",
    )
    p1.rotation_deg = 15.0
    p2.rotation_deg = 30.0
    for pad, pin in ((p1, "1"), (p2, "2")):
        pad.provenance.add_evidence(
            Evidence("gerber_x2_component_refdes", "U7", 1.0)
        )
        pad.provenance.add_evidence(
            Evidence("gerber_x2_pin_number", pin, 1.0)
        )

    board = BoardModel(
        pads=[p1, p2],
        nets=[
            NetGroup("N1", ["BP1"], 1.0, "A"),
            NetGroup("N2", ["BP2"], 1.0, "B"),
        ],
        components=[
            ComponentHypothesis(
                "CMP_U7",
                ["BP1", "BP2"],
                "gerber_x2_component",
                1.0,
                ["source-proven Gerber X2 .P"],
                reference="U7",
                source_pin_map={"BP1": "1", "BP2": "2"},
            )
        ],
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-bottom.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '(footprint "PHOTONX:RecoveredX2Component" (layer "B.Cu")' in text
    assert '(pad "1" smd rect (at 0.000000 0.000000 -15.000000)' in text
    assert '(pad "2" smd rect (at 2.500000 -1.500000 -30.000000)' in text

    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_equivalent"] is True


def test_duplicate_x2_component_ids_fail_closed_before_uuid_generation(tmp_path):
    def component(refdes, prefix, x_offset, net_prefix):
        pads = []
        pin_map = {}
        nets = []
        for index, dx in enumerate((0.0, 2.0), start=1):
            pad_id = f"{prefix}{index}"
            net_id = f"{net_prefix}{index}"
            pad = PadCandidate(
                pad_id,
                Point(x_offset + dx, 10.0),
                1.0,
                1.0,
                "C",
                "F.Cu",
                None,
                net_id,
            )
            pad.provenance.add_evidence(
                Evidence("gerber_x2_component_refdes", refdes, 1.0)
            )
            pad.provenance.add_evidence(
                Evidence("gerber_x2_pin_number", str(index), 1.0)
            )
            pads.append(pad)
            pin_map[pad_id] = str(index)
            nets.append(NetGroup(net_id, [pad_id], 1.0, net_id))
        hypothesis = ComponentHypothesis(
            "CMP_DUPLICATE",
            [pad.id for pad in pads],
            "gerber_x2_component",
            1.0,
            ["source-proven Gerber X2 .P"],
            reference=refdes,
            source_pin_map=pin_map,
        )
        return pads, nets, hypothesis

    pads_a, nets_a, component_a = component("U1", "A", 0.0, "NA")
    pads_b, nets_b, component_b = component("U2", "B", 20.0, "NB")
    board = BoardModel(
        pads=[*pads_a, *pads_b],
        nets=[*nets_a, *nets_b],
        components=[component_a, component_b],
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-duplicate-component-id.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredX2Component" not in text
    assert text.count('(footprint "PHOTONX:RecoveredPad"') == 4
    issues = [
        item
        for item in report.issues
        if item.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
        and item.object_id == "CMP_DUPLICATE"
    ]
    assert len(issues) == 2
    assert all(
        "component ID is duplicated across source-proven X2 components"
        in item.message
        for item in issues
    )

    audit = compare_kicad_connectivity(
        board,
        read_kicad_board_text(text),
        report,
    )
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True
