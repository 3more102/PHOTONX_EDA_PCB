from dataclasses import dataclass,field
@dataclass(frozen=True)
class BoardSchematicTrace:
    object_type:str
    object_id:str
    page_ids:tuple[str,...]=()
    net_ids:tuple[str,...]=()
    component_ids:tuple[str,...]=()
@dataclass
class BoardSchematicTraceability:
    traces:list[BoardSchematicTrace]=field(default_factory=list)
