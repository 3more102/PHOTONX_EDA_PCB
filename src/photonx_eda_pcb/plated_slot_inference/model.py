from dataclasses import dataclass
@dataclass(frozen=True)
class PlatedSlotPadstack:
    slot_id:str
    center:tuple[float,float]
    angle_deg:float
    pad_size:tuple[float,float]
    pad_shape:str
    drill_size:tuple[float,float]
    layers:tuple[str,...]
    net_id:str|None
    pad_ids:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
@dataclass(frozen=True)
class PadstackInference:
    slot_id:str
    padstack:PlatedSlotPadstack|None
    blockers:tuple[str,...]=()
