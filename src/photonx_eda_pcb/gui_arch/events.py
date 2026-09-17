from dataclasses import dataclass
@dataclass(frozen=True)
class UiEvent: name:str; payload:dict
