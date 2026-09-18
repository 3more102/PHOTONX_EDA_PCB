from photonx_eda_pcb.kicad_reader import read_kicad_board_text

def test_reader_parses_oval_drill_dimensions():
    text='''(kicad_pcb (version 20240108)
      (layers (0 "F.Cu" signal) (44 "Edge.Cuts" user))
      (footprint "X" (layer "F.Cu") (at 10 20 30)
        (pad "" np_thru_hole oval (at 1 2 15) (size 5 1) (drill oval 5 1) (layers "*.Cu" "*.Mask"))))
    '''
    b=read_kicad_board_text(text)
    p=b["footprints"][0]["pads"][0]
    assert p["drill_shape"]=="oval" and p["drill_size"]==(5.0,1.0)
    assert p["angle"]==15.0 and b["footprints"][0]["angle"]==30.0
    assert len(b["mechanical_slots"])==1
