from dataclasses import dataclass,field
@dataclass
class PluginContext:
    project:object|None=None
    services:dict[str,object]=field(default_factory=dict)
    permissions:dict[str,bool]=field(default_factory=dict)
