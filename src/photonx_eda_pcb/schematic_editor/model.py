from dataclasses import dataclass,field
@dataclass(frozen=True)
class EditorSymbol:
    id:str
    component_id:str
    library_id:str
    reference:str
    value:str
    x:float
    y:float
    rotation:float=0.0
    page_id:str="root"
    confidence:float=0.0
@dataclass(frozen=True)
class EditorWire:
    id:str
    net_id:str
    points:tuple[tuple[float,float],...]
    page_id:str="root"
@dataclass(frozen=True)
class EditorLabel:
    id:str
    net_id:str
    text:str
    x:float
    y:float
    page_id:str="root"
    global_label:bool=False
@dataclass(frozen=True)
class EditorBus:
    id:str
    name:str
    net_ids:tuple[str,...]
    points:tuple[tuple[float,float],...]
    page_id:str="root"
@dataclass
class EditorPage:
    id:str
    title:str
    symbol_ids:list[str]=field(default_factory=list)
    wire_ids:list[str]=field(default_factory=list)
    label_ids:list[str]=field(default_factory=list)
    bus_ids:list[str]=field(default_factory=list)
@dataclass
class EditorDocument:
    pages:dict[str,EditorPage]=field(default_factory=dict)
    symbols:dict[str,EditorSymbol]=field(default_factory=dict)
    wires:dict[str,EditorWire]=field(default_factory=dict)
    labels:dict[str,EditorLabel]=field(default_factory=dict)
    buses:dict[str,EditorBus]=field(default_factory=dict)
    metadata:dict[str,object]=field(default_factory=dict)
