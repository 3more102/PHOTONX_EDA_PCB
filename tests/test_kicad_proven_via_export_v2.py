from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, DrillHit, NetGroup, PadCandidate, Point, Track
from photonx_eda_pcb.roundtrip.kicad_connectivity import compare_kicad_connectivity


def _net(net_id, label):
    return NetGroup(net_id, [], 1.0, label)


def _span(*pad_ids):
    return {
        "drill_id": "D1",
        "from_layer": "F.Cu",
        "to_layer": "B.Cu",
        "confidence": 0.95,
        "proven": True,
        "pad_ids": list(pad_ids),
        "evidence": ["plated drill with exact pad support"],
    }


def _pad(pad_id, layer, size=1.0, net_id="N1"):
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


def test_proven_via_requires_support_on_every_spanned_declared_layer(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        tracks=[
            Track("T_IN1", Point(2, 0), Point(3, 0), 0.2, "In1.Cu", "N1"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert readback["vias"] == []
    assert report.exported_via_span_ids == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_LAYER_SUPPORT_INCOMPLETE"
        and issue.object_id == "D1"
        for issue in report.issues
    )
    data = omission_manifest(report)
    assert data["exported_via_spans"] == []
    assert data["omitted_via_spans"] == ["D1"]
    assert validate_omission_manifest(data) == []


def test_proven_via_rejects_mismatched_annular_diameters(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu", 1.0),
            _pad("P_B", "B.Cu", 1.2),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert readback["vias"] == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_ANNULUS_UNREPRESENTABLE"
        and issue.object_id == "D1"
        for issue in report.issues
    )


def test_proven_via_rejects_supporting_pad_net_conflict(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND"), _net("N2", "VCC")],
        pads=[
            _pad("P_F", "F.Cu", net_id="N1"),
            _pad("P_B", "B.Cu", net_id="N2"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert readback["vias"] == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_NET_CONFLICT"
        and issue.object_id == "D1"
        for issue in report.issues
    )


def test_exact_multilayer_proven_via_exports_through_declared_inner_layer(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_I1", "In1.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_I1", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert len(readback["vias"]) == 1
    assert readback["vias"][0]["layers"] == ("F.Cu", "B.Cu")
    assert readback["vias"][0]["size"] == 1.0
    assert readback["vias"][0]["drill"] == 0.4
    assert readback["vias"][0]["net"] == 1
    assert readback["vias"][0]["locked"] is False
    assert readback["vias"][0]["remove_unused_layers"] is False
    assert readback["vias"][0]["keep_end_layers"] is False
    assert readback["vias"][0]["free"] is False
    assert report.exported_via_span_ids == ["D1"]
    assert report.skipped_via_span_ids == []
    assert audit["vias"]["equal"] is True
    assert audit["source_equivalent"] is True


def test_roundtrip_detects_exported_via_geometry_drift(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["vias"][0]["size"] = 1.1

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["vias"]["equal"] is False
    assert audit["vias"]["missing"]
    assert audit["vias"]["unexpected"]
    assert audit["roundtrip_equal"] is False
    assert audit["source_equivalent"] is False



def test_partial_layer_proven_span_is_not_mislabeled_as_through_via(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_I1", "In1.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={
            "via_spans": [
                {
                    "drill_id": "D1",
                    "from_layer": "F.Cu",
                    "to_layer": "In1.Cu",
                    "confidence": 0.95,
                    "proven": True,
                    "pad_ids": ["P_F", "P_I1"],
                    "evidence": ["partial plated span"],
                }
            ]
        },
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert readback["vias"] == []
    assert report.exported_via_span_ids == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_TYPE_UNPROVEN"
        and issue.object_id == "D1"
        for issue in report.issues
    )
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_roundtrip_detects_exported_via_type_drift(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    assert readback["vias"][0]["type"] == "through"
    readback["vias"][0]["type"] = "blind"

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["vias"]["equal"] is False
    assert audit["roundtrip_equal"] is False
    assert audit["source_equivalent"] is False



def _add_via_flag(text, flag):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.lstrip().startswith("(via "):
            marker = "(net 1)"
            assert marker in line
            token = flag if flag == "locked" else f"({flag})"
            lines[index] = line.replace(marker, f"{token} {marker}", 1)
            return "\n".join(lines) + "\n"
    raise AssertionError("export did not contain a via")


def test_roundtrip_detects_exported_via_behavior_flag_drift(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    original = path.read_text(encoding="utf-8")

    for flag in ("locked", "remove_unused_layers", "free"):
        readback = read_kicad_board_text(_add_via_flag(original, flag))
        assert readback["vias"][0][flag] is True

        audit = compare_kicad_connectivity(board, readback, report)

        assert audit["vias"]["equal"] is False
        assert audit["roundtrip_equal"] is False
        assert audit["source_equivalent"] is False


def test_roundtrip_rejects_keep_end_layers_without_remove_unused_layers(tmp_path):
    board = BoardModel(
        nets=[_net("N1", "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={"via_spans": [_span("P_F", "P_B")]},
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    mutated = _add_via_flag(
        path.read_text(encoding="utf-8"),
        "keep_end_layers",
    )
    readback = read_kicad_board_text(mutated)

    assert readback["vias"][0]["keep_end_layers"] is True
    assert readback["vias"][0]["remove_unused_layers"] is False

    audit = compare_kicad_connectivity(board, readback, report)

    assert any(
        issue["code"] == "KICAD_ROUNDTRIP_INVALID_VIA_BEHAVIOR"
        for issue in audit["issues"]
    )
    assert audit["roundtrip_equal"] is False
    assert audit["source_equivalent"] is False
