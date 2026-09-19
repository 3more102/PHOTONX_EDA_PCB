from dataclasses import dataclass

from .compare import compare_metrics


@dataclass(frozen=True)
class CorpusResult:
    case_id: str
    passed: bool
    differences: tuple[tuple, ...] = ()
    observed: dict | None = None
    ignored_unknowns: tuple[str, ...] = ()


def run_case(case, executor):
    observed = dict(executor(case))
    unknowns = tuple(case.expectation.unknowns)
    differences = tuple(
        compare_metrics(
            case.expectation.metrics,
            observed,
            case.expectation.tolerances,
            unknowns=unknowns,
        )
    )
    ignored_unknowns = tuple(sorted(set(observed).intersection(unknowns)))
    return CorpusResult(
        case.id,
        not differences,
        differences,
        observed,
        ignored_unknowns,
    )


def run_corpus(corpus, executor):
    return [
        run_case(case, executor)
        for case in sorted(corpus.cases, key=lambda item: item.id)
    ]
