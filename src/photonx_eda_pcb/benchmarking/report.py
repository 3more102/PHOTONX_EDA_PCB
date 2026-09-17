from .statistics import duration_stats
def result_report(result):return {'name':result.name,'ok':result.ok,'error':result.error,'metadata':result.metadata,'stats':duration_stats(result.durations)}
def suite_report(results):return {'cases':[result_report(r) for r in results],'passed':sum(r.ok for r in results),'failed':sum(not r.ok for r in results)}
