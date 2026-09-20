from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


def test_edge_cuts_guard_rejects_direct_non_graphic_item():
    text = """
    (kicad_pcb
      (layers
        (0 "F.Cu" signal)
        (31 "B.Cu" signal)
        (36 "B.SilkS" user "b.silkscreen")
        (37 "F.SilkS" user "f.silkscreen")
        (44 "Edge.Cuts" user)
      )
      (net 0 "")
      (dimension
        (type aligned)
        (layer "Edge.Cuts")
        (uuid 00000000-0000-0000-0000-000000000091)
      )
    )
    """

    readback = read_kicad_board_text(text)

    assert readback["unexpected_edge_graphics"] == [
        {
            "type": "dimension",
            "uuid": "00000000-0000-0000-0000-000000000091",
            "root_index": 2,
        }
    ]

    audit = compare_kicad_connectivity(BoardModel(), readback)

    assert audit["roundtrip_equal"] is False
    assert audit["unexpected_edge_graphics"]["equal"] is False
    assert audit["unexpected_edge_graphics"]["observed_count"] == 1
    assert audit["unexpected_edge_graphics"]["unexpected"] == [
        {
            "type": "dimension",
            "uuid": "00000000-0000-0000-0000-000000000091",
        }
    ]


def test_edge_cuts_guard_still_allows_photonx_gr_line_family():
    text = """
    (kicad_pcb
      (layers
        (0 "F.Cu" signal)
        (31 "B.Cu" signal)
        (44 "Edge.Cuts" user)
      )
      (net 0 "")
      (gr_line
        (start 0 0)
        (end 1 0)
        (stroke (width 0.05) (type default))
        (layer "Edge.Cuts")
        (uuid 00000000-0000-0000-0000-000000000090)
      )
    )
    """

    readback = read_kicad_board_text(text)

    assert readback["unexpected_edge_graphics"] == []
    assert len(readback["edge_graphics"]) == 1
