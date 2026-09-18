from dataclasses import dataclass,field
@dataclass(frozen=True)
class LearnedRule:
    name:str
    value:float
    confidence:float
    sample_count:int
@dataclass
class LearnedProfile:
    name:str
    rules:dict[str,LearnedRule]=field(default_factory=dict)
