from dataclasses import dataclass
@dataclass
class ExcellonModalState:
    x:float=0.0
    y:float=0.0
    tool:int|None=None
    units:str='mm'
    routing:bool=False
