from .labels import split_indexed_label
from .model import BusCandidate
def infer_buses(labels,min_width=2):
    groups={}
    for net_id,label in labels.items():
        parsed=split_indexed_label(label)
        if parsed is None:continue
        base,index=parsed
        groups.setdefault(base,[]).append((index,str(net_id)))
    out=[]
    for base,items in sorted(groups.items()):
        uniq={i:n for i,n in items}
        if len(uniq)<int(min_width):continue
        indices=tuple(sorted(uniq));nets=tuple(uniq[i] for i in indices)
        contiguous=indices==tuple(range(min(indices),max(indices)+1))
        confidence=.85 if contiguous else .65
        ev=("indexed_labels","contiguous_indices") if contiguous else ("indexed_labels",)
        out.append(BusCandidate(base,nets,indices,len(indices),confidence,ev))
    return out
