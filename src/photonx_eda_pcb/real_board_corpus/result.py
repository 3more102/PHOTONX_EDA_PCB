from dataclasses import dataclass
@dataclass(frozen=True)
class CorpusResult:
    case_id:str
    passed:bool
    metric_failures:int=0
    net_failures:int=0
    diagnostics:tuple[str,...]=()
