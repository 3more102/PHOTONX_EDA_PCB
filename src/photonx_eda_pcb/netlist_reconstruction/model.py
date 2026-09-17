from dataclasses import dataclass,field

@dataclass(frozen=True)
class NetConnection:
    component_id:str
    pin_id:str

@dataclass
class Netlist:
    nets:dict[str,list[NetConnection]]=field(default_factory=dict)
    labels:dict[str,str]=field(default_factory=dict)
