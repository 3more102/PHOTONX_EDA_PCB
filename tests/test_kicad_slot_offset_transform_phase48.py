from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.roundtrip.mechanical import canonical_slot

def test_reader_applies_footprint_and_pad_rotation():
    text='''(kicad_pcb (version 20240108)
      (layers (0 "F.Cu" signal) (44 "Edge.Cuts" user))
      (footprint "X" (layer "F.Cu") (at 10 20 90)
        (pad "" np_thru_hole oval (at 2 0 0) (size 5 1) (drill oval 5 1) (layers "*.Cu" "*.Mask"))))
    '''
    slot=read_kicad_board_text(text)["mechanical_slots"][0]
    c=canonical_slot(slot)
    assert c[:4]==(10.0,22.0,5.0,1.0)
