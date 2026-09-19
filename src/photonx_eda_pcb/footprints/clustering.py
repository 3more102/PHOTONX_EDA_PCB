from math import hypot

from photonx_eda_pcb.spatial_connectivity.points import (
    build_point_index,
    radius_candidate_pairs,
)


def cluster_pads_bruteforce(pads, max_gap_mm=5.0):
    remaining = {p.id: p for p in pads}
    groups = []
    while remaining:
        seed_id = sorted(remaining)[0]
        group = [remaining.pop(seed_id)]
        changed = True
        while changed:
            changed = False
            for pid, p in list(remaining.items()):
                if any(
                    hypot(
                        p.center.x - q.center.x,
                        p.center.y - q.center.y,
                    )
                    <= max_gap_mm
                    for q in group
                ):
                    group.append(remaining.pop(pid))
                    changed = True
        groups.append(sorted(group, key=lambda p: p.id))
    return groups


def cluster_pads(
    pads,
    max_gap_mm=5.0,
    *,
    use_spatial_index=True,
    cell_size_mm=None,
    spatial_backend="auto",
):
    pads = list(pads)
    if not use_spatial_index:
        return cluster_pads_bruteforce(pads, max_gap_mm)
    if not pads:
        return []

    by = {p.id: p for p in pads}
    idx = build_point_index(
        ((p.id, p) for p in pads),
        lambda p: (p.center.x, p.center.y),
        float(cell_size_mm or max(1.0, max_gap_mm)),
    )
    adjacency = {pid: [] for pid in by}
    for distance, first, second in radius_candidate_pairs(
        idx,
        max_gap_mm,
        backend=spatial_backend,
    ):
        adjacency[first].append((distance, second))
        adjacency[second].append((distance, first))
    for neighbors in adjacency.values():
        neighbors.sort(key=lambda item: (item[0], item[1]))

    unvisited = set(by)
    groups = []
    while unvisited:
        seed = min(unvisited)
        queue = [seed]
        unvisited.remove(seed)
        group = []
        while queue:
            pid = queue.pop(0)
            group.append(by[pid])
            for _, nid in adjacency[pid]:
                if nid in unvisited:
                    unvisited.remove(nid)
                    queue.append(nid)
        groups.append(sorted(group, key=lambda p: p.id))
    return groups
