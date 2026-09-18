from dataclasses import dataclass,field
@dataclass
class CorpusCase:
    id:str
    input_paths:list[str]=field(default_factory=list)
    expected_metrics:dict[str,float|int]=field(default_factory=dict)
    expected_nets:dict[str,list[str]]=field(default_factory=dict)
    notes:str=""
