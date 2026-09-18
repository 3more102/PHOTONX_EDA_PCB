from dataclasses import dataclass
@dataclass(frozen=True)
class FpgaPin:
    pin:str
    net_id:str|None
    bank:str
    io_standard:str|None=None
    voltage:float|None=None
@dataclass(frozen=True)
class FpgaBank:
    component_id:str
    bank:str
    pins:tuple[FpgaPin,...]
    supply_voltage:float|None
    confidence:float
