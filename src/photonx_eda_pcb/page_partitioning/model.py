from dataclasses import dataclass
@dataclass(frozen=True)
class PagePartition:
    id:str
    title:str
    block_ids:tuple[str,...]
    component_ids:tuple[str,...]
    net_ids:tuple[str,...]
    weight:int
