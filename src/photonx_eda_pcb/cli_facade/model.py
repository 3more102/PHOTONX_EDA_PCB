from dataclasses import dataclass,field
@dataclass(frozen=True)
class CliRequest:
    command:str
    args:tuple[str,...]=()
    options:dict=field(default_factory=dict)
@dataclass
class CliResponse:
    success:bool
    data:object=None
    error:str=""
    exit_code:int=0
