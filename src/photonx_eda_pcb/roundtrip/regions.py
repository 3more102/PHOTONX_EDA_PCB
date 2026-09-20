def _point_xy(point):
    if hasattr(point, "x") and hasattr(point, "y"):
        return float(point.x), float(point.y)
    return float(point[0]), float(point[1])


def canonical_ring(points):
    coords = [(round(x, 6), round(y, 6)) for x, y in map(_point_xy, points)]
    if len(coords) > 1 and coords[0] == coords[-1]:
        coords = coords[:-1]
    if len(coords) < 3 or len(set(coords)) < 3:
        raise ValueError("region ring requires at least three distinct vertices")

    variants = []
    for sequence in (coords, list(reversed(coords))):
        variants.extend(
            tuple(sequence[offset:] + sequence[:offset])
            for offset in range(len(sequence))
        )
    return min(variants)


def _expected_net_names(board):
    return {net.id: (net.label or net.id) for net in board.nets}


def canonical_expected_region(region, net_names):
    if region.net_id is None:
        net_name = ""
    else:
        net_name = net_names.get(region.net_id, f"<unresolved:{region.net_id}>")
    return (
        str(region.id),
        str(region.layer),
        str(net_name),
        canonical_ring(region.points),
        tuple(sorted(canonical_ring(hole) for hole in getattr(region, "holes", ()))),
    )


def canonical_observed_zone(zone):
    layer = zone.get("layer")
    if layer is None:
        raise ValueError("round-trip copper-region comparison requires a single-layer zone")

    name = zone.get("name")
    region_id = str(name)[len("PHOTONX:") :] if isinstance(name, str) and name.startswith("PHOTONX:") else str(name or "")
    net = zone.get("net")
    net_name = "" if net in (None, 0) else str(zone.get("net_name") or "")
    return (
        region_id,
        str(layer),
        net_name,
        canonical_ring(zone["outline"]),
        tuple(sorted(canonical_ring(hole) for hole in zone.get("holes", ()))),
    )


def compare_kicad_copper_regions(board, observed_zones, region_ids=None):
    net_names = _expected_net_names(board)
    selected = None if region_ids is None else {str(item) for item in region_ids}
    expected = sorted(
        canonical_expected_region(region, net_names)
        for region in getattr(board, "regions", ())
        if selected is None or str(region.id) in selected
    )
    observed = sorted(canonical_observed_zone(zone) for zone in observed_zones)
    return {
        "equal": expected == observed,
        "expected": expected,
        "observed": observed,
        "missing": sorted(set(expected) - set(observed)),
        "unexpected": sorted(set(observed) - set(expected)),
    }
