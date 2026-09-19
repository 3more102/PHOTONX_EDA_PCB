from .query import child, children


def read_zones(root):
    out = []
    for zone in children(root, "zone"):
        net = child(zone, "net")
        net_name = child(zone, "net_name")
        layer = child(zone, "layer")
        name = child(zone, "name")
        uuid = child(zone, "uuid")
        out.append(
            {
                "net": int(net[1]) if net and len(net) >= 2 else None,
                "net_name": str(net_name[1]) if net_name and len(net_name) >= 2 else None,
                "layer": str(layer[1]) if layer and len(layer) >= 2 else None,
                "name": str(name[1]) if name and len(name) >= 2 else None,
                "uuid": str(uuid[1]) if uuid and len(uuid) >= 2 else None,
            }
        )
    return out
