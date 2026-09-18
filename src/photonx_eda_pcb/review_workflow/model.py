from dataclasses import dataclass,field
@dataclass
class ReviewItem:
    id:str
    kind:str
    object_id:str
    priority:int=0
    status:str="open"
    assignee:str=""
    decision:str=""
    notes:list[str]=field(default_factory=list)
@dataclass
class ReviewQueue:
    items:list[ReviewItem]=field(default_factory=list)
