from __future__ import annotations
from shapely.geometry import LineString, Point as SPoint, box
from ..models import Track, PadCandidate


def copper_shape(obj: Track | PadCandidate):
    if isinstance(obj, Track):
        return LineString([(obj.start.x, obj.start.y), (obj.end.x, obj.end.y)]).buffer(obj.width / 2.0, cap_style=1)
    if obj.shape == "C":
        return SPoint(obj.center.x, obj.center.y).buffer(obj.size_x / 2.0)
    return box(obj.center.x - obj.size_x / 2.0, obj.center.y - obj.size_y / 2.0, obj.center.x + obj.size_x / 2.0, obj.center.y + obj.size_y / 2.0)
