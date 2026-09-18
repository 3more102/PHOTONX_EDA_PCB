from .model import EdgeSegment
def from_outline_segments(outline):
    out=[]
    for s in outline:
        out.append(EdgeSegment(str(s.id),(float(s.start.x),float(s.start.y)),(float(s.end.x),float(s.end.y))))
    return out
