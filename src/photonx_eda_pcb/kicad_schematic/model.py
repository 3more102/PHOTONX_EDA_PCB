from dataclasses import dataclass,field
@dataclass(frozen=True)
class KicadSymbol:
    reference:str
    value:str
    library_id:str
    x:float
    y:float
    rotation:float=0.0
@dataclass(frozen=True)
class KicadWire:
    start:tuple[float,float]
    end:tuple[float,float]
@dataclass
class KicadSchematic:
    symbols:list[KicadSymbol]=field(default_factory=list)
    wires:list[KicadWire]=field(default_factory=list)
    labels:list[tuple[str,float,float]]=field(default_factory=list)
