from .query import child, children


def read_edge_graphics(root):
    out = []
    for index, graphic in enumerate(children(root, "gr_line")):
        layer = child(graphic, "layer")
        if not layer or str(layer[1]) != "Edge.Cuts":
            continue
        start = child(graphic, "start")
        end = child(graphic, "end")
        stroke = child(graphic, "stroke")
        width = child(stroke, "width") if stroke else None
        stroke_type = child(stroke, "type") if stroke else None
        uuid = child(graphic, "uuid")
        if start is None or len(start) < 3 or end is None or len(end) < 3:
            raise ValueError(f"Edge.Cuts gr_line {index} requires start/end coordinates")
        out.append(
            {
                "start": (float(start[1]), float(start[2])),
                "end": (float(end[1]), float(end[2])),
                "layer": "Edge.Cuts",
                "width": float(width[1]) if width and len(width) >= 2 else None,
                "stroke_type": (
                    str(stroke_type[1])
                    if stroke_type and len(stroke_type) >= 2
                    else None
                ),
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
            }
        )
    return out


def read_edge_lines(root):
    return [
        (item["start"], item["end"])
        for item in read_edge_graphics(root)
    ]


def read_unexpected_edge_graphics(root):
    out = []
    if not isinstance(root, list):
        return out
    for index, item in enumerate(root[1:]):
        if not isinstance(item, list) or not item:
            continue
        token = str(item[0])
        if not token.startswith("gr_") or token == "gr_line":
            continue
        layer = child(item, "layer")
        if not layer or len(layer) < 2 or str(layer[1]) != "Edge.Cuts":
            continue
        uuid = child(item, "uuid")
        out.append(
            {
                "type": token,
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
                "root_index": index,
            }
        )
    return out



_FABRICATION_GRAPHIC_LAYERS = {
    "F.Mask",
    "B.Mask",
    "F.Paste",
    "B.Paste",
}


def _is_fabrication_graphic_layer(name):
    return str(name) in _FABRICATION_GRAPHIC_LAYERS


def _is_canonical_copper_layer(name):
    layer = str(name)
    if layer in {"F.Cu", "B.Cu"}:
        return True
    if not (layer.startswith("In") and layer.endswith(".Cu")):
        return False
    number = layer[2:-3]
    return number.isdigit() and 1 <= int(number) <= 30


def read_unexpected_copper_graphics(root):
    out = []
    if not isinstance(root, list):
        return out
    allowed_direct_copper_items = {"segment", "arc", "zone", "footprint"}
    for index, item in enumerate(root[1:]):
        if not isinstance(item, list) or not item:
            continue
        token = str(item[0])
        if token in allowed_direct_copper_items:
            continue
        layer = child(item, "layer")
        if not layer or len(layer) < 2:
            continue
        layer_name = str(layer[1])
        if not _is_canonical_copper_layer(layer_name):
            continue
        uuid = child(item, "uuid")
        out.append(
            {
                "type": token,
                "layer": layer_name,
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
                "root_index": index,
            }
        )
    return out


def read_unexpected_fabrication_graphics(root):
    out = []
    if not isinstance(root, list):
        return out
    for index, item in enumerate(root[1:]):
        if not isinstance(item, list) or not item:
            continue
        token = str(item[0])
        layer = child(item, "layer")
        if not layer or len(layer) < 2:
            continue
        layer_name = str(layer[1])
        if not _is_fabrication_graphic_layer(layer_name):
            continue
        uuid = child(item, "uuid")
        out.append(
            {
                "type": token,
                "layer": layer_name,
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
                "root_index": index,
            }
        )
    return out
