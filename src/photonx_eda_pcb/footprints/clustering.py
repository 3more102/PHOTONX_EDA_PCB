from collections import deque
from math import hypot,isfinite
from photonx_eda_pcb.spatial_connectivity.points import build_point_index,radius_queries

def _distance(a,b):
    return hypot(a.center.x-b.center.x,a.center.y-b.center.y)

def _normalize_cluster_span(value):
    if value is None:return None
    span=float(value)
    if not isfinite(span) or span<=0:raise ValueError("max_cluster_span_mm must be a positive finite value")
    return span

def _split_group_by_span(group,max_cluster_span_mm):
    group=sorted(group,key=lambda p:p.id)
    if max_cluster_span_mm is None:return [group]
    buckets=[]
    for pad in group:
        candidates=[]
        for index,bucket in enumerate(buckets):
            farthest=max((_distance(pad,other) for other in bucket),default=0.0)
            if farthest<=max_cluster_span_mm:
                candidates.append((farthest,tuple(other.id for other in bucket),index))
        if candidates:
            buckets[min(candidates)[2]].append(pad)
        else:
            buckets.append([pad])
    return [sorted(bucket,key=lambda p:p.id) for bucket in buckets]

def cluster_pads_bruteforce(pads,max_gap_mm=5.0,*,max_cluster_span_mm=None):
    max_cluster_span_mm=_normalize_cluster_span(max_cluster_span_mm)
    remaining={p.id:p for p in pads};groups=[]
    while remaining:
        seed_id=sorted(remaining)[0];group=[remaining.pop(seed_id)];changed=True
        while changed:
            changed=False
            for pid,p in list(remaining.items()):
                if any(_distance(p,q)<=max_gap_mm for q in group):
                    group.append(remaining.pop(pid));changed=True
        groups.extend(_split_group_by_span(group,max_cluster_span_mm))
    return groups

def cluster_pads(pads,max_gap_mm=5.0,*,use_spatial_index=True,cell_size_mm=None,backend="auto",max_cluster_span_mm=None):
    pads=list(pads)
    if not use_spatial_index:return cluster_pads_bruteforce(pads,max_gap_mm,max_cluster_span_mm=max_cluster_span_mm)
    max_cluster_span_mm=_normalize_cluster_span(max_cluster_span_mm)
    if not pads:return []
    by={p.id:p for p in pads}
    idx=build_point_index(((p.id,p) for p in pads),lambda p:(p.center.x,p.center.y),float(cell_size_mm or max(1.0,max_gap_mm)))
    neighbor_lists=radius_queries(idx,((p.center.x,p.center.y,max_gap_mm) for p in pads),backend=backend)
    neighbors={p.id:items for p,items in zip(pads,neighbor_lists)}
    unvisited=set(by);groups=[]
    while unvisited:
        seed=min(unvisited);queue=deque([seed]);unvisited.remove(seed);group=[]
        while queue:
            pid=queue.popleft();p=by[pid];group.append(p)
            for _,nid in neighbors[pid]:
                if nid in unvisited:
                    unvisited.remove(nid);queue.append(nid)
        groups.extend(_split_group_by_span(group,max_cluster_span_mm))
    return groups
