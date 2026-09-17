from dataclasses import dataclass
@dataclass(frozen=True)
class BomItem:
    references:tuple[str,...]
    value:str=""
    footprint:str=""
    mpn:str=""
    manufacturer:str=""
    quantity:int|None=None
