from dataclasses import dataclass,field
@dataclass(frozen=True)
class RegressionCase:
    name:str; input_dir:str; expected:dict=field(default_factory=dict); tags:tuple[str,...]=()
