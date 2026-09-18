from dataclasses import dataclass
@dataclass(frozen=True)
class DiagnosticDefinition:
    code:str
    severity:str
    title:str
    description:str=""
    remediation:str=""
