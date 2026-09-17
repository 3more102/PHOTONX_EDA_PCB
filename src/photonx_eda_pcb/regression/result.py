from dataclasses import dataclass,field
@dataclass
class RegressionResult:
    name:str; passed:bool; failures:list[str]=field(default_factory=list); observed:dict=field(default_factory=dict)
