from photonx_eda_pcb.parser_conformance import ConformanceCase,ConformanceExpectation,run_conformance_case
def test_permissive_unsupported_is_diagnostic():
    c=ConformanceCase("region","gerber","%FSLAX24Y24*%\n%MOMM*%\nG36*\nM02*\n",ConformanceExpectation({"tracks":0},("UNSUPPORTED_GERBER_CONSTRUCT",)),strict=False)
    r=run_conformance_case(c)
    assert r.passed and "UNSUPPORTED_GERBER_CONSTRUCT" in r.diagnostics
