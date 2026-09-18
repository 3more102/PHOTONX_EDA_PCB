from photonx_eda_pcb.parser_conformance.library import builtin_cases
from photonx_eda_pcb.parser_conformance import (
    run_conformance_suite,
    validate_conformance_case,
)
from photonx_eda_pcb.parser_conformance.report import conformance_summary


def test_builtin_parser_conformance_suite():
    cases = builtin_cases()
    assert all(validate_conformance_case(c) == [] for c in cases)
    results = run_conformance_suite(cases)
    summary = conformance_summary(results)
    assert summary["failed"] == 0
    assert summary["passed"] == len(cases)


def test_builtin_conformance_declares_g75_arc_boundary():
    results = {r.id: r for r in run_conformance_suite(builtin_cases())}
    arc = results["gerber-g75-ccw-arc"]
    assert arc.passed
    assert arc.counts["tracks"] == 8
    assert arc.exception_type is None
