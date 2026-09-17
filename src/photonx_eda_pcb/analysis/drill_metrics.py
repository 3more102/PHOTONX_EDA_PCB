from collections import Counter
from ..models import BoardModel
def drill_diameter_histogram(board:BoardModel,precision:int=3)->dict[float,int]: return dict(Counter(round(d.diameter,precision) for d in board.drills))
def unknown_plating_count(board:BoardModel)->int: return sum(d.plating=="unknown" for d in board.drills)
