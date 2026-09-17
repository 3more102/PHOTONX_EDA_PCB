from math import hypot

def cluster_pads(pads,max_gap_mm=5.0):
    remaining={p.id:p for p in pads}; groups=[]
    while remaining:
        seed_id=sorted(remaining)[0]; group=[remaining.pop(seed_id)]; changed=True
        while changed:
            changed=False
            for pid,p in list(remaining.items()):
                if any(hypot(p.center.x-q.center.x,p.center.y-q.center.y)<=max_gap_mm for q in group):
                    group.append(remaining.pop(pid)); changed=True
        groups.append(sorted(group,key=lambda p:p.id))
    return groups
