from .footprints import read_footprints
from .graphics import read_edge_lines
from .layers import read_layers
from .mechanical_slots import read_mechanical_slots
from .nets import read_nets
from .segments import read_segments
from .sexpr import parse_sexpr
from .vias import read_vias


def _validate_net_references(nets, segments, vias, footprints):
    known = {net["code"] for net in nets}

    for kind, items in (("segment", segments), ("via", vias)):
        for item in items:
            code = item["net"]
            if code is not None and code not in known:
                raise ValueError(
                    f"{kind} references undefined net ordinal {code}"
                )

    for footprint in footprints:
        for pad in footprint["pads"]:
            code = pad["net"]
            if code is not None and code not in known:
                raise ValueError(
                    f"pad references undefined net ordinal {code}"
                )


def read_kicad_board_text(text):
    root = parse_sexpr(text)
    if not isinstance(root, list) or not root or root[0] != "kicad_pcb":
        raise ValueError("not a kicad_pcb document")

    nets = read_nets(root)
    segments = read_segments(root)
    vias = read_vias(root)
    footprints = read_footprints(root)
    _validate_net_references(nets, segments, vias, footprints)

    return {
        "layers": read_layers(root),
        "nets": nets,
        "segments": segments,
        "vias": vias,
        "footprints": footprints,
        "edge_lines": read_edge_lines(root),
        "mechanical_slots": read_mechanical_slots(footprints),
    }
