from dataclasses import dataclass
@dataclass(frozen=True)
class GeoPoint: x:float; y:float
@dataclass(frozen=True)
class LinePrimitive: start:GeoPoint; end:GeoPoint; width:float=0.0
@dataclass(frozen=True)
class FlashPrimitive: center:GeoPoint; shape:str; x:float; y:float|None=None
@dataclass(frozen=True)
class PolygonPrimitive: points:tuple[GeoPoint,...]
