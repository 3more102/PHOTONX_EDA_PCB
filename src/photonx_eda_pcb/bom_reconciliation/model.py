from dataclasses import dataclass
@dataclass(frozen=True)
class BomRecord:
    reference:str
    value:str=""
    footprint:str=""
    mpn:str=""
@dataclass(frozen=True)
class BomDiscrepancy:
    reference:str
    code:str
    expected:str=""
    observed:str=""
