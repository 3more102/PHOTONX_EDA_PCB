from dataclasses import dataclass
@dataclass(frozen=True)
class DiagnosticRecord:
    severity:str
    code:str
    message:str
    source:str|None=None
    line:int|None=None
