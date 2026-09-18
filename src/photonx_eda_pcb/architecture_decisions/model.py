from dataclasses import dataclass
@dataclass(frozen=True)
class ArchitectureDecision:
    id:str
    title:str
    status:str
    context:str
    decision:str
    consequences:tuple[str,...]=()
