from photonx_eda_pcb.kicad_reader.validation import validate_board_dict
def test_warn_edge(): assert ('warning','KICAD_EDGE_MISSING') in validate_board_dict({'nets':[]})
