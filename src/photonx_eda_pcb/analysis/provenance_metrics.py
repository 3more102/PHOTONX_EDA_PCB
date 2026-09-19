from ..core.board_objects import iter_physical_objects
from ..models import BoardModel

def _physical_objects(board):
    return list(iter_physical_objects(board))

def source_coverage(board:BoardModel)->float:
    objs=_physical_objects(board)
    return 0.0 if not objs else sum(bool(getattr(o,"provenance",None) and o.provenance.sources) for o in objs)/len(objs)

def evidence_count(board:BoardModel)->int:
    objs=[*_physical_objects(board),*board.nets]
    return sum(len(o.provenance.evidence) for o in objs if hasattr(o,"provenance"))
