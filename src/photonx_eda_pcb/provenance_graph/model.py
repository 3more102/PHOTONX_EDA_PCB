from dataclasses import dataclass,field
@dataclass(frozen=True)
class ProvenanceNode:
    id:str
    kind:str
    label:str=""
@dataclass(frozen=True)
class ProvenanceEdge:
    source:str
    target:str
    relation:str
    confidence:float=1.0
@dataclass
class ProvenanceGraph:
    nodes:dict[str,ProvenanceNode]=field(default_factory=dict)
    edges:list[ProvenanceEdge]=field(default_factory=list)
