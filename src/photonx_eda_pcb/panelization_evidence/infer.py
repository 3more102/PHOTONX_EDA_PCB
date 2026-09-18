from .model import PanelHypothesis,RepeatedBoard
from .repetition import repeated_groups
def infer_panel(board_bounds,tooling_holes=()):
    groups=repeated_groups(board_bounds);boards=[]
    for gi,g in enumerate(groups):
        boards.extend(RepeatedBoard(f"rep{gi}_{i}",tuple(map(float,b))) for i,b in enumerate(g))
    evidence=[];score=0.0
    if boards:evidence.append("repeated_board_bounds");score+=0.7
    holes=list(tooling_holes)
    if len(holes)>=2:evidence.append("tooling_holes");score+=0.2
    return PanelHypothesis(boards,None,round(min(score,1),12),evidence)
