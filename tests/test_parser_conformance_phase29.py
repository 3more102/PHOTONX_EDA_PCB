from photonx_eda_pcb.parser_conformance.library import builtin_cases
from photonx_eda_pcb.parser_conformance import run_conformance_suite,validate_conformance_case
from photonx_eda_pcb.parser_conformance.report import conformance_summary
def test_builtin_parser_conformance_suite():
    cases=builtin_cases()
    assert all(validate_conformance_case(c)==[] for c in cases)
    r=run_conformance_suite(cases);s=conformance_summary(r)
    assert s["failed"]==0 and s["passed"]==len(cases)
