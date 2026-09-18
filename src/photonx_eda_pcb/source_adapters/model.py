from dataclasses import dataclass,field
@dataclass
class SourceDocument:
    path:str
    format:str
    content:object
    metadata:dict[str,object]=field(default_factory=dict)
