from dataclasses import dataclass,field
@dataclass(frozen=True)
class ChannelDelta:
    group_id:str
    instance_id:str
    code:str
    detail:str
@dataclass
class ChannelConsistencyReport:
    deltas:list[ChannelDelta]=field(default_factory=list)
    consistent:bool=True
