from dataclasses import dataclass

@dataclass(frozen=True)
class SilkToken:
    text:str
    x:float=0.0
    y:float=0.0
    rotation_deg:float=0.0
    layer:str='F.SilkS'
