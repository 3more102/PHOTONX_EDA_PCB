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


def test_structured_pin_map_drift_from_provenance_fails_closed(tmp_path):
    board = _board()
    board.components[0].source_pin_map = {"P1": "A1", "P2": "B2"}

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-stale-structured-pin-map.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredX2Component" not in text
    assert text.count('(footprint "PHOTONX:RecoveredPad"') == 2
    assert any(
        item.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
        and "structured source pin number does not match trusted X2 evidence"
        in item.message
        for item in report.issues
    )


def test_structured_pin_function_drift_from_provenance_fails_closed(tmp_path):
    board = _board()
    board.components[0].source_pin_functions["P2"] = "RESET"

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-stale-structured-pin-function.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredX2Component" not in text
    assert text.count('(footprint "PHOTONX:RecoveredPad"') == 2
    assert any(
        item.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
        and "structured source pin function does not match trusted X2 evidence"
        in item.message
        for item in report.issues
    )


def test_structured_pin_function_without_provenance_fails_closed(tmp_path):
    board = _board()
    p2 = board.pads[1]
    p2.provenance.evidence = [
        item
        for item in p2.provenance.evidence
        if item.kind != "gerber_x2_pin_function"
    ]

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2-unbacked-structured-pin-function.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert "PHOTONX:RecoveredX2Component" not in text
    assert text.count('(footprint "PHOTONX:RecoveredPad"') == 2
    assert any(
        item.code == "KICAD_X2_COMPONENT_IDENTITY_NOT_GROUPED"
        and "structured source pin function lacks matching trusted X2 evidence"
        in item.message
        for item in report.issues
    )
