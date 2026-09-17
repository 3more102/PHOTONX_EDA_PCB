from dataclasses import dataclass
@dataclass(frozen=True)
class WorkspaceCommand:
    name:str
    payload:dict
def command(name,**payload): return WorkspaceCommand(str(name),payload)
