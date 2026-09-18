from dataclasses import dataclass
@dataclass(frozen=True)
class SymbolPin:
    number:str
    name:str=""
    electrical_type:str="passive"
@dataclass(frozen=True)
class SymbolEntry:
    name:str
    kind:str
    pins:tuple[SymbolPin,...]
    reference_prefix:str="U"
