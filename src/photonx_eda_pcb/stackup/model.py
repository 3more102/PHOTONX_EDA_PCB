from dataclasses import dataclass, field, asdict
@dataclass(frozen=True)
class LayerSpec:
    name:str; role:str; order:int; copper:bool=False; thickness_mm:float|None=None; source:str='inferred'
@dataclass
class StackupModel:
    layers:list[LayerSpec]=field(default_factory=list)
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)
    def ordered(self): return sorted(self.layers,key=lambda x:x.order)
    def copper_layers(self): return [x for x in self.ordered() if x.copper]
    def to_dict(self): return {'layers':[asdict(x) for x in self.ordered()],'confidence':self.confidence,'evidence':list(self.evidence)}
