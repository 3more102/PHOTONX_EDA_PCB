from photonx_eda_pcb.parser_conformance import ConformanceCase,ConformanceExpectation,run_conformance_case
def test_conformance_reports_count_mismatch():
    c=ConformanceCase("bad-expectation","excellon","M48\nMETRIC\nT01C0.8\n%\nT01\nX1Y1\nM30\n",ConformanceExpectation({"drills":2}))
    r=run_conformance_case(c)
    assert not r.passed and any(x.startswith("count:drills") for x in r.differences)
