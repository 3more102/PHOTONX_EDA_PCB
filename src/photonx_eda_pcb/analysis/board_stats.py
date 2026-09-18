from ..models import BoardModel
from ..geometry.measure import total_track_length,total_outline_length
from ..excellon_routing.measure import route_length_mm
def board_stats(board:BoardModel)->dict[str,int|float]:
    return {"tracks":len(board.tracks),"pads":len(board.pads),"drills":len(board.drills),"slots":len(getattr(board,"slots",())),"routes":len(getattr(board,"routes",())),"outline_segments":len(board.outline),"nets":len(board.nets),"components":len(board.components),"diagnostics":len(board.diagnostics),"track_length_mm":round(total_track_length(board),6),"route_length_mm":round(sum(route_length_mm(r) for r in getattr(board,"routes",())),6),"outline_length_mm":round(total_outline_length(board),6)}
