from dataclasses import dataclass,field
@dataclass
class HierarchyBlock:
    id:str
    name:str
    component_ids:list[str]=field(default_factory=list)
    net_ids:list[str]=field(default_factory=list)
    confidence:float=0.0
    evidence:list[str]=field(default_factory=list)
@dataclass
class HierarchyResult:
    blocks:list[HierarchyBlock]=field(default_factory=list)
    unassigned_components:list[str]=field(default_factory=list)
