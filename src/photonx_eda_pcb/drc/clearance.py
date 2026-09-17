from shapely.geometry import Point as SPoint,LineString
from .model import DrcIssue

def _shape(o):
    if hasattr(o,'start'):return LineString([(o.start.x,o.start.y),(o.end.x,o.end.y)]).buffer(o.width/2)
    return SPoint(o.center.x,o.center.y).buffer(max(o.size_x,o.size_y)/2)

def check_clearance(board,cfg):
    objs=[*board.tracks,*board.pads]; out=[]; shapes={o.id:_shape(o) for o in objs}
    for i,a in enumerate(objs):
        for b in objs[i+1:]:
            if getattr(a,'layer',None)!=getattr(b,'layer',None):continue
            if a.net_id is None or b.net_id is None or a.net_id==b.net_id:continue
            if shapes[a.id].distance(shapes[b.id])<cfg.min_clearance_mm:out.append(DrcIssue('error','COPPER_CLEARANCE',f'clearance below {cfg.min_clearance_mm} mm',(a.id,b.id)))
    return out
