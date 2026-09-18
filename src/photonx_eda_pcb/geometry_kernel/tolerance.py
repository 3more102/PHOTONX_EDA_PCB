from dataclasses import dataclass
@dataclass(frozen=True)
class GeometryTolerance:
    contact_mm:float=.03
    coordinate_mm:float=1e-6
    containment_mm:float=1e-9
    def validate(self):
        return [] if min(self.contact_mm,self.coordinate_mm,self.containment_mm)>=0 else ["GEOMETRY_TOLERANCE_NEGATIVE"]
