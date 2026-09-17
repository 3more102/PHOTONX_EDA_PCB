from dataclasses import dataclass,field
@dataclass(frozen=True)
class RepairCandidate:
    kind:str;object_ids:tuple[str,...];confidence:float;reason:str;automatic:bool=False;metadata:dict=field(default_factory=dict)
