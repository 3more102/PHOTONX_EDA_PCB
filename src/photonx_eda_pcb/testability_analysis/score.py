def testability_score(report):
    coverage=float(report.metrics.get("net_test_coverage",0));exposed=float(report.metrics.get("exposed_fraction",0))
    return round(.75*coverage+.25*exposed,6)
