from dataclasses import dataclass,field
@dataclass
class PanelState:
    id:str
    visible:bool=True
    dock:str="left"
    size:int=250
@dataclass
class DocumentTab:
    id:str
    title:str
    path:str=""
    dirty:bool=False
@dataclass
class DesktopState:
    panels:dict[str,PanelState]=field(default_factory=dict)
    tabs:list[DocumentTab]=field(default_factory=list)
    active_tab:str|None=None
    status_message:str=""
