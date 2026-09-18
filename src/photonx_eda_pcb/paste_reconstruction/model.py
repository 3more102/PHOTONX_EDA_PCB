from dataclasses import dataclass
@dataclass(frozen=True)
class PasteAperture:
    id:str
    center:tuple[float,float]
    size:tuple[float,float]
    layer:str="F.Paste"
    source_id:str|None=None
