from dataclasses import dataclass
@dataclass(frozen=True)
class PatternDefinition:
    name:str
    required_kinds:tuple[str,...]
    min_components:int=1
    max_components:int|None=None
    required_roles:tuple[str,...]=()
    description:str=""
@dataclass(frozen=True)
class PatternMatch:
    pattern:str
    object_id:str
    score:float
    evidence:tuple[str,...]=()
