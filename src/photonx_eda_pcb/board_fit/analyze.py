from .model import BoardFitEvidence
from .margins import edge_margins
def analyze_board_fit(board_bounds,enclosure_bounds,confidence=.5):
    m=edge_margins(board_bounds,enclosure_bounds);fits=min(m)>=0;notes=[]
    if not fits:notes.append("board_exceeds_enclosure")
    if min(m)>=0 and min(m)<.5:notes.append("tight_clearance")
    return BoardFitEvidence(tuple(map(float,board_bounds)),tuple(map(float,enclosure_bounds)),tuple(round(x,6) for x in m),fits,round(min(1,max(0,float(confidence))),6),notes)
