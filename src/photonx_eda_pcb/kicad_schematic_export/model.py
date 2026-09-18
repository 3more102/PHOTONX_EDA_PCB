from dataclasses import dataclass,field
@dataclass(frozen=True)
class ExportSymbol:
    id:str
    library_id:str
    reference:str
    value:str
    x:float
    y:float
    rotation:float=0.0
    footprint:str=""
@dataclass(frozen=True)
class ExportWire:
    id:str
    net_id:str
    points:tuple[tuple[float,float],...]
@dataclass(frozen=True)
class ExportLabel:
    id:str
    text:str
    x:float
    y:float
    global_label:bool=False
@dataclass
class ExportDocument:
    project_name:str="PHOTONX"
    root_uuid:str=""
    version:int=20231120
    symbols:list[ExportSymbol]=field(default_factory=list)
    wires:list[ExportWire]=field(default_factory=list)
    labels:list[ExportLabel]=field(default_factory=list)
