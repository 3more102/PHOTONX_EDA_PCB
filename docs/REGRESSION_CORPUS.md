# Regression Corpus

Corpus cases declare input artifacts, expected metrics, numeric tolerances,
intentionally unknown fields, and whether a fixture is synthetic. External
cases require separate dataset source/license metadata.

## Assertion boundary

CorpusExpectation.metrics is the set of facts a case asserts. The runner
compares those keys against the executor output and reports missing, unexpected,
or mismatched values. Numeric keys may opt into absolute tolerances through
CorpusExpectation.tolerances.

CorpusExpectation.unknowns is different: it records metric names that the
source evidence cannot establish and that the case intentionally does not
assert. A declared unknown is ignored by the comparison whether the executor
returns it or omits it. The raw observed value is still retained in
CorpusResult.observed, and returned unknown keys are listed in
CorpusResult.ignored_unknowns for auditability.

Unknowns are exact top-level metric names, not wildcards. Any undeclared extra
metric remains an unexpected difference.

## Validation rules

Corpus validation rejects ambiguous expectation contracts:

- an unknown metric may not also appear in metrics;
- duplicate or empty unknown names are invalid;
- a tolerance must refer to an asserted metric;
- tolerances must be finite numeric values greater than or equal to zero.

These checks keep the corpus evidence-safe: an explicitly unknown semantic is
not promoted to ground truth merely because an executor happens to emit a
value.
