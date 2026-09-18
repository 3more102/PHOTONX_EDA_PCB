from dataclasses import dataclass
@dataclass(frozen=True)
class PackageEntry:
    name:str
    family:str
    pin_count:int
    pitch_mm:float|None=None
    body_width_mm:float|None=None
    body_height_mm:float|None=None
    mounting:str="unknown"
