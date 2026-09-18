from photonx_eda_pcb.incremental_pipeline import StageSpec
from photonx_eda_pcb.invalidation_audit import InvalidationExpectation,audit_invalidation
def test_invalidation_expectation_matches_plan():
    s=[StageSpec("parse"),StageSpec("geometry",("parse",)),StageSpec("nets",("geometry",)),StageSpec("report",("nets",))]
    r=audit_invalidation(s,InvalidationExpectation(("geometry",),("geometry","nets","report")))
    assert r.passed and not r.missing and not r.unexpected
