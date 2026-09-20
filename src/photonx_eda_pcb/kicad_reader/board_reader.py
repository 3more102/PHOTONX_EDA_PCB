from .sexpr import parse_sexpr
from .layers import read_layers
from .nets import read_nets
from .segments import read_segments
from .track_arcs import read_track_arcs
from .vias import read_vias
from .footprints import read_footprints
from .graphics import read_edge_graphics, read_unexpected_copper_graphics, read_unexpected_edge_graphics
from .mechanical_slots import read_mechanical_slots
from .zones import read_zones


def read_kicad_board_text(text):
    root = parse_sexpr(text)
    if not isinstance(root, list) or not root or root[0] != "kicad_pcb":
        raise ValueError("not a kicad_pcb document")
    footprints = read_footprints(root)
    edge_graphics = read_edge_graphics(root)
    return {
        "layers": read_layers(root),
        "nets": read_nets(root),
        "segments": read_segments(root),
        "track_arcs": read_track_arcs(root),
        "vias": read_vias(root),
        "zones": read_zones(root),
        "footprints": footprints,
        "edge_lines": [(item["start"], item["end"]) for item in edge_graphics],
        "edge_graphics": edge_graphics,
        "unexpected_edge_graphics": read_unexpected_edge_graphics(root),
        "unexpected_copper_graphics": read_unexpected_copper_graphics(root),
        "mechanical_slots": read_mechanical_slots(footprints),
    }
