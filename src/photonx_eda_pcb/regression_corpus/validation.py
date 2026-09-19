from math import isfinite

from .catalog import CATEGORIES


def validate_corpus(corpus):
    issues = []
    ids = set()

    for case in corpus.cases:
        if case.id in ids:
            issues.append("CORPUS_DUPLICATE_ID")
        ids.add(case.id)

        if not case.inputs:
            issues.append("CORPUS_NO_INPUTS")
        if case.category not in CATEGORIES:
            issues.append("CORPUS_UNKNOWN_CATEGORY")
        if not case.expectation.metrics:
            issues.append("CORPUS_NO_EXPECTATIONS")
        if not case.synthetic and not case.description:
            issues.append("CORPUS_EXTERNAL_MISSING_DESCRIPTION")

        seen_unknowns = set()
        for key in case.expectation.unknowns:
            if not isinstance(key, str) or not key.strip():
                issues.append("CORPUS_INVALID_UNKNOWN")
                continue
            if key in seen_unknowns:
                issues.append("CORPUS_DUPLICATE_UNKNOWN")
            seen_unknowns.add(key)
            if key in case.expectation.metrics:
                issues.append("CORPUS_UNKNOWN_EXPECTATION_CONFLICT")

        for key, value in case.expectation.tolerances.items():
            if key not in case.expectation.metrics:
                issues.append("CORPUS_TOLERANCE_WITHOUT_EXPECTATION")
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                issues.append("CORPUS_INVALID_TOLERANCE")
                continue
            if not isfinite(numeric):
                issues.append("CORPUS_INVALID_TOLERANCE")
            elif numeric < 0:
                issues.append("CORPUS_NEGATIVE_TOLERANCE")

    return issues
