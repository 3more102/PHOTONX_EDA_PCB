from dataclasses import dataclass
@dataclass(frozen=True)
class StageSpec:
    name:str
    dependencies:tuple[str,...]=()
    version:str="1"
@dataclass(frozen=True)
class StageState:
    name:str
    input_key:str
    output_key:str
    cached:bool
