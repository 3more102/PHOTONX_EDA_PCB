from dataclasses import dataclass,field
@dataclass
class BoardFitEvidence:
    board_bounds:tuple[float,float,float,float]
    enclosure_bounds:tuple[float,float,float,float]
    edge_margins:tuple[float,float,float,float]
    fits:bool
    confidence:float
    notes:list[str]=field(default_factory=list)
