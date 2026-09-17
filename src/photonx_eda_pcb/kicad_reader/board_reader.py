from .sexpr import parse_sexpr
from .layers import read_layers
from .nets import read_nets
from .segments import read_segments
from .vias import read_vias
from .footprints import read_footprints
from .graphics import read_edge_lines
def read_kicad_board_text(text):
    root=parse_sexpr(text)
    if not isinstance(root,list) or not root or root[0]!='kicad_pcb': raise ValueError('not a kicad_pcb document')
    return {'layers':read_layers(root),'nets':read_nets(root),'segments':read_segments(root),'vias':read_vias(root),'footprints':read_footprints(root),'edge_lines':read_edge_lines(root)}
