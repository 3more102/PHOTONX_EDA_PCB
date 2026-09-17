from dataclasses import dataclass,field
@dataclass
class ViaSpanCandidate:
    drill_id:str; from_layer:str|None; to_layer:str|None; confidence:float; evidence:list[str]=field(default_factory=list); proven:bool=False
    def layers(self): return tuple(x for x in (self.from_layer,self.to_layer) if x is not None)
