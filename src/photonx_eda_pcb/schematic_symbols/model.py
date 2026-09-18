from dataclasses import dataclass,field
@dataclass(frozen=True)
class PinDefinition:
    number:str
    name:str=""
    electrical_type:str="passive"
@dataclass
class SymbolHypothesis:
    component_id:str
    library_id:str
    confidence:float
    pins:list[PinDefinition]=field(default_factory=list)
    evidence:list[str]=field(default_factory=list)
