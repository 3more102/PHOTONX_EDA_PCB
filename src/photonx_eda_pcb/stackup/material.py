from dataclasses import dataclass
@dataclass(frozen=True)
class MaterialHint:
    name:str; er:float|None=None; loss_tangent:float|None=None; confidence:float=0.0
COMMON={'FR4':MaterialHint('FR4',4.2,0.02,0.35),'RO4350B':MaterialHint('RO4350B',3.48,0.0037,0.35)}
def material_hint(name:str): return COMMON.get(name.upper())
