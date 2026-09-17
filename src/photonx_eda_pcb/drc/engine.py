from .model import DrcIssue,DrcConfig
from .widths import check_track_widths
from .drills import check_drills
from .annular import check_annular_ring
from .clearance import check_clearance
from .edge import check_edge_presence
from .duplicates import check_duplicate_ids
RULES=(check_track_widths,check_drills,check_annular_ring,check_clearance,check_edge_presence,check_duplicate_ids)
def run_drc(board,cfg=None):
    cfg=cfg or DrcConfig(); out=[]
    for rule in RULES:out.extend(rule(board,cfg))
    return out
