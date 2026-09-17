from dataclasses import dataclass,field
@dataclass
class CommandResult:
    exit_code:int=0
    message:str=''
    data:dict=field(default_factory=dict)
