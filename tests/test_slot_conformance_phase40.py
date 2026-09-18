from photonx_eda_pcb.parser_conformance.library import builtin_cases
from photonx_eda_pcb.parser_conformance import run_conformance_suite

def test_conformance_suite_contains_passing_g85_case():
    results={r.id:r for r in run_conformance_suite(builtin_cases())}
    assert results["excellon-g85-slot"].passed
    assert results["excellon-g85-slot"].counts["slots"]==1
