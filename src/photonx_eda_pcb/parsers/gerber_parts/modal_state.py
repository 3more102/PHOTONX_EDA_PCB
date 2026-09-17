from dataclasses import dataclass
@dataclass
class GerberModalState:
    x:float=0.0
    y:float=0.0
    aperture:int|None=None
    interpolation:str='linear'
    polarity:str='dark'
    region:bool=False
    units:str='mm'
