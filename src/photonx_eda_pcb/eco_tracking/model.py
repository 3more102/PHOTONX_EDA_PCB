from dataclasses import dataclass,field
@dataclass(frozen=True)
class EcoChange:
    id:str
    category:str
    object_id:str
    action:str
    summary:str=""
    approved:bool=False
@dataclass
class EcoSet:
    name:str
    changes:list[EcoChange]=field(default_factory=list)
    metadata:dict[str,object]=field(default_factory=dict)
