RANK={"info":0,"warning":1,"error":2,"critical":3}
def validation_passed(report,block_at="error"):
    threshold=RANK[str(block_at)]
    return not any((not r.passed) and RANK.get(r.severity,2)>=threshold for r in report.results)
def blocking_results(report,block_at="error"):
    threshold=RANK[str(block_at)]
    return [r for r in report.results if (not r.passed) and RANK.get(r.severity,2)>=threshold]
