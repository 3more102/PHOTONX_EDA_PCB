from ..models import BoardModel
def source_coverage(board:BoardModel)->float:
    objs=[*board.tracks,*board.pads,*board.drills,*board.outline]
    return 0.0 if not objs else sum(bool(o.provenance.sources) for o in objs)/len(objs)
def evidence_count(board:BoardModel)->int:
    objs=[*board.tracks,*board.pads,*board.drills,*board.outline,*board.nets]
    return sum(len(o.provenance.evidence) for o in objs if hasattr(o,"provenance"))
