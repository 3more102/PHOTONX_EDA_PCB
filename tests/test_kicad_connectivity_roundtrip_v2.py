from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    NetGroup,
    PadCandidate,
    Point,
    Track,
)
from photonx_eda_pcb.roundtrip import (
    compare_kicad_connectivity,
    validate_kicad_connectivity_roundtrip,
)


def _net(net_id="N1", label="GND"):
    return NetGroup(net_id, [], 1.0, label)


def _full_board():
    return BoardModel(
        nets=[_net()],
        tracks=[Track("T1", Point(0, 0), Point(4, 0), 0.25, "F.Cu", "N1")],
        pads=[
            PadCandidate("P1", Point(0, 0), 1.2, 1.2, "C", "F.Cu", None, "N1")
        ],
        regions=[
            CopperRegion(
                "R1",
                (Point(1, 1), Point(3, 1), Point(3, 3), Point(1, 3)),
                "F.Cu",
                "N1",
            )
        ],
        slots=[SlotFeature("S1", (5, 0), (7, 0), 1.0, "non-plated")],
    )


def test_kicad_connectivity_roundtrip_covers_regions_and_slots(tmp_path):
    board = _full_board()
    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")

    audit = validate_kicad_connectivity_roundtrip(board, path, report)

    assert audit["scope"] == [
        "net_table",
        "tracks",
        "recovered_pads",
        "copper_regions",
        "recovered_slots",
    ]
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is True
    assert audit["source_equivalent"] is True
    assert audit["regions"]["equal"] is True
    assert audit["regions"]["expected_count"] == 1
    assert audit["slots"]["equal"] is True
    assert audit["slots"]["expected_count"] == 1
    assert audit["issues"] == []


def test_kicad_connectivity_roundtrip_detects_zone_net_drift(tmp_path):
    board = _full_board()
    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["zones"][0]["net"] = 0

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["regions"]["equal"] is False
    assert audit["regions"]["missing"][0]["net"] == {"code": 1, "name": "GND"}
    assert audit["regions"]["unexpected"][0]["net"] == {"code": 0, "name": ""}


def test_kicad_connectivity_roundtrip_detects_slot_net_claim(tmp_path):
    board = _full_board()
    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    slot_fp = next(
        fp
        for fp in readback["footprints"]
        if fp["name"] == "PHOTONX:RecoveredNPTHSlot"
    )
    slot_fp["pads"][0]["net"] = 1

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["slots"]["equal"] is False


def test_kicad_connectivity_roundtrip_separates_policy_losses_from_readback(tmp_path):
    board = BoardModel(
        nets=[_net()],
        tracks=[
            Track("T1", Point(0, 0), Point(2, 0), 0.25, "F.Cu", "N1"),
            Track("T_SKIP", Point(0, 1), Point(2, 1), 0.25, "F.Cu", "MISSING"),
        ],
        pads=[
            PadCandidate(
                "P_UNRESOLVED",
                Point(1, 1),
                1.0,
                1.0,
                "R",
                "F.Cu",
                None,
                "MISSING",
            )
        ],
        regions=[
            CopperRegion(
                "R_SKIP",
                (Point(3, 1), Point(5, 1), Point(5, 3), Point(3, 3)),
                "F.Cu",
                "MISSING",
            )
        ],
        slots=[SlotFeature("S_SKIP", (6, 0), (8, 0), 1.0, "unknown")],
    )

    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    audit = validate_kicad_connectivity_roundtrip(board, path, report)

    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"] == {
        "skipped_track_ids": ["T_SKIP"],
        "skipped_region_ids": ["R_SKIP"],
        "skipped_slot_ids": ["S_SKIP"],
        "unresolved_pad_net_ids": ["P_UNRESOLVED"],
        "unresolved_slot_net_ids": [],
    }


def test_kicad_connectivity_roundtrip_detects_changed_track_net(tmp_path):
    board = BoardModel(
        nets=[_net()],
        tracks=[Track("T1", Point(0, 0), Point(2, 0), 0.25, "F.Cu", "N1")],
    )
    path, report = export_kicad_with_report(board, tmp_path / "board.kicad_pcb")
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    readback["segments"][0]["net"] = 0

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["roundtrip_equal"] is False
    assert audit["tracks"]["equal"] is False
