from ..models import BoardModel
def completeness_score(board:BoardModel)->float:
    checks=[bool(board.tracks or board.pads),bool(board.outline),bool(board.nets),bool(board.components),bool(board.metadata)]
    return sum(checks)/len(checks)
def completeness_breakdown(board:BoardModel)->dict[str,bool]:
    return {"physical_geometry":bool(board.tracks or board.pads),"outline":bool(board.outline),"nets":bool(board.nets),"component_hypotheses":bool(board.components),"metadata":bool(board.metadata)}
