from dataclasses import dataclass
@dataclass(frozen=True)
class InputProtectionPath:
    connector_id:str
    target_id:str
    protection_components:tuple[str,...]
    kinds:tuple[str,...]
    confidence:float
    evidence:tuple[str,...]=()
