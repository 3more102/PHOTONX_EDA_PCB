from dataclasses import dataclass
@dataclass(frozen=True)
class RoundTripTolerance:
    coordinate_mm:float=1e-5; width_mm:float=1e-5
