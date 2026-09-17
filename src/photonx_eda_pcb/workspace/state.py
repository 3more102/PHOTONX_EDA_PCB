from dataclasses import dataclass,field
@dataclass
class WorkspaceState:
    project_name:str
    source_root:str
    active_board:str|None=None
    dirty:bool=False
    metadata:dict=field(default_factory=dict)
