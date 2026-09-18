from dataclasses import dataclass,field
@dataclass
class ExternalInterfaceMap:
    connectors:dict[str,dict]=field(default_factory=dict)
    ports:list=field(default_factory=list)
    protection:list=field(default_factory=list)
    confidence:float=0.0
    unresolved:list[str]=field(default_factory=list)
