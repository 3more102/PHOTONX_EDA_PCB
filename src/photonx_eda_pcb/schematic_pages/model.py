from dataclasses import dataclass,field
@dataclass(frozen=True)
class SchematicPage:
    id:str
    title:str
    components:tuple[str,...]
    nets:tuple[str,...]
    block_kind:str="unknown"
@dataclass
class SchematicPageSet:
    pages:list[SchematicPage]=field(default_factory=list)
