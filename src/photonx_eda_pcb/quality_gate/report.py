def gate_report(result):return {'passed':result.passed,'metrics':dict(sorted(result.metrics.items())),'findings':[x.__dict__ for x in result.findings]}
def gate_text(result):return ('PASS' if result.passed else 'FAIL')+f' | findings={len(result.findings)}'
