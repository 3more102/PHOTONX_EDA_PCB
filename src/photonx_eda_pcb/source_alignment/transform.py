from dataclasses import dataclass
@dataclass(frozen=True)
class AlignmentTransform:
    dx:float=0.0
    dy:float=0.0
    scale:float=1.0
    rotation_deg:float=0.0
