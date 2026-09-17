from dataclasses import dataclass,field
@dataclass
class GroundTruth:
    object_counts:dict[str,int]=field(default_factory=dict); net_members:dict[str,set[str]]=field(default_factory=dict); metadata:dict=field(default_factory=dict)
