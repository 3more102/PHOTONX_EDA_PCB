from photonx_eda_pcb.parser_conformance import ConformanceCase,ConformanceExpectation,run_conformance_case

def test_permissive_unsupported_is_diagnostic():
    c=ConformanceCase(
        "aperture-block",
        "gerber",
        "%FSLAX24Y24*%\n%MOMM*%\n%ABD10*%\n%AB*%\nM02*\n",
        ConformanceExpectation({"tracks":0},("UNSUPPORTED_GERBER_APERTURE_BLOCK",)),
        strict=False,
    )
    r=run_conformance_case(c)
    assert r.passed and "UNSUPPORTED_GERBER_APERTURE_BLOCK" in r.diagnostics
