from dataclasses import dataclass,field
@dataclass(frozen=True)
class Annotation:
    id:str
    object_id:str
    text:str
    author:str=""
    category:str="note"
    resolved:bool=False
@dataclass
class AnnotationStore:
    items:list[Annotation]=field(default_factory=list)
