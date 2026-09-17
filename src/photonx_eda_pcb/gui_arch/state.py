from dataclasses import dataclass,field
@dataclass
class AppState:
    selected_id:str|None=None; highlighted_net:str|None=None; visible_layers:set[str]=field(default_factory=set); zoom:float=1.0; pan_x:float=0.0; pan_y:float=0.0; status:str=''
