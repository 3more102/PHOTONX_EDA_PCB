from dataclasses import dataclass
@dataclass(frozen=True)
class WorkspaceView:
    component_count:int
    net_count:int
    block_count:int
    page_count:int
    unresolved_count:int
    review_count:int
