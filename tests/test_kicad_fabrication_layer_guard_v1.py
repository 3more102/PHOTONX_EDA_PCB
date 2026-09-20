from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


def test_board_fabrication_guard_rejects_non_graphic_direct_item():
    text = """
    (kicad_pcb
      (dimension
        (type aligned)
        (layer "F.Mask")
        (uuid 00000000-0000-0000-0000-000000000101)
      )
    )
    """

    readback = read_kicad_board_text(text)

    assert readback["unexpected_fabrication_graphics"] == [
        {
            "type": "dimension",
            "layer": "F.Mask",
            "uuid": "00000000-0000-0000-0000-000000000101",
            "root_index": 0,
        }
    ]

    audit = compare_kicad_connectivity(BoardModel(), readback)

    assert audit["unexpected_fabrication_graphics"]["equal"] is False
    assert audit["unexpected_fabrication_graphics"]["observed_count"] == 1
    assert audit["roundtrip_equal"] is False


def test_footprint_fabrication_guard_rejects_non_fp_child():
    text = """
    (kicad_pcb
      (footprint "PHOTONX:RecoveredPad"
        (layer "F.Cu")
        (uuid 00000000-0000-0000-0000-000000000102)
        (at 0 0)
        (property "Reference" "P1")
        (dimension
          (type aligned)
          (layer "B.Paste")
          (uuid 00000000-0000-0000-0000-000000000103)
        )
      )
    )
    """

    readback = read_kicad_board_text(text)
    unexpected = readback["footprints"][0]["unexpected_fabrication_graphics"]

    assert unexpected == [
        {
            "type": "dimension",
            "layer": "B.Paste",
            "uuid": "00000000-0000-0000-0000-000000000103",
            "child_index": 4,
        }
    ]

    audit = compare_kicad_connectivity(BoardModel(), readback)

    assert audit["unexpected_fabrication_graphics"]["equal"] is False
    assert audit["unexpected_fabrication_graphics"]["observed_count"] == 1
    assert audit["roundtrip_equal"] is False
