from dataclasses import dataclass,field
@dataclass(frozen=True)
class ComponentNode:
    id:str
    kind:str="unknown"
@dataclass(frozen=True)
class NetNode:
    id:str
    label:str|None=None
@dataclass
class SchematicGraph:
    components:dict[str,ComponentNode]=field(default_factory=dict)
    nets:dict[str,NetNode]=field(default_factory=dict)
    pin_edges:list[tuple[str,str,str]]=field(default_factory=list)
