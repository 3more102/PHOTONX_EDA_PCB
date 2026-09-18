from dataclasses import dataclass,field
@dataclass
class ProjectSession:
    project_name:str
    root:str=""
    active_board:str|None=None
    open_documents:list[str]=field(default_factory=list)
    settings:dict[str,object]=field(default_factory=dict)
    dirty:bool=False
    revision:int=0
