from dataclasses import dataclass,field

@dataclass(frozen=True)
class DiffEntry:
    kind:str
    object_id:str
    before:object=None
    after:object=None

@dataclass
class BoardDiff:
    entries:list[DiffEntry]=field(default_factory=list)
