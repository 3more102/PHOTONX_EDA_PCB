from dataclasses import dataclass,field
@dataclass
class ViaTransition:
    id:str
    net_id:str|None
    start_layer:str
    end_layer:str
    drill_mm:float
    pad_mm:float
    nearby_return_vias:int=0
    stub_layers:int=0
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)
