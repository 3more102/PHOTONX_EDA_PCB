from photonx_eda_pcb.kicad_reader.board_reader import read_kicad_board_text
def test_reader():
    d=read_kicad_board_text('(kicad_pcb (net 1 GND) (segment (start 0 0) (end 1 0) (width 0.25) (layer F.Cu) (net 1)) (gr_line (start 0 0) (end 1 0) (layer Edge.Cuts)))'); assert len(d['nets'])==1; assert len(d['segments'])==1; assert len(d['edge_lines'])==1
