from dataclasses import dataclass,field
@dataclass(frozen=True)
class ValidationCheck:
    name:str
    severity:str="error"
    group:str="general"
@dataclass(frozen=True)
class ValidationResult:
    name:str
    passed:bool
    severity:str
    messages:tuple[str,...]=()
@dataclass
class ValidationReport:
    results:list[ValidationResult]=field(default_factory=list)
