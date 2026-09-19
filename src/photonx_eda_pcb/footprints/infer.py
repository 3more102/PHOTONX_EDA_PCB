from .clustering import cluster_pads
from .matcher import match_signature
from .orientation import principal_orientation_deg
from .candidate import FootprintCandidate

def infer_footprints(board,max_gap_mm=5.0,*,max_cluster_span_mm=None,backend="auto"):
    out=[]
    for i,g in enumerate(cluster_pads(board.pads,max_gap_mm,max_cluster_span_mm=max_cluster_span_mm,backend=backend),1):
        m=match_signature(g)
        out.append(FootprintCandidate(f'FP?{i}',[p.id for p in g],m['best'],m['confidence'],principal_orientation_deg(g),[f"matched {m['best']} from {len(g)} pads"]))
    return out
