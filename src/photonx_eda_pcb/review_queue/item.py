from dataclasses import dataclass,field
@dataclass
class ReviewItem:
    id:str
    kind:str
    target_id:str
    reason:str
    confidence:float=0.0
    status:str="open"
    decision:str|None=None
    metadata:dict=field(default_factory=dict)
