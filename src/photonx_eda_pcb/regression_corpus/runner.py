from dataclasses import dataclass
from .compare import compare_metrics
@dataclass(frozen=True)
class CorpusResult:
    case_id:str
    passed:bool
    differences:tuple[tuple,...]=()
    observed:dict|None=None
def run_case(case,executor):
    observed=dict(executor(case))
    diff=tuple(compare_metrics(case.expectation.metrics,observed,case.expectation.tolerances))
    return CorpusResult(case.id,not diff,diff,observed)
def run_corpus(corpus,executor):return [run_case(c,executor) for c in sorted(corpus.cases,key=lambda x:x.id)]
