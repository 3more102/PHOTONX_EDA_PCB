from .result import CorpusResult
from .metrics import compare_metrics
def evaluate_case(case,actual_metrics,actual_nets=None):
    m=compare_metrics(case.expected_metrics,actual_metrics)
    mf=sum(v["status"]!="pass" for v in m.values())
    nf=0
    if actual_nets is not None:
        from .net_compare import compare_nets
        n=compare_nets(case.expected_nets,actual_nets);nf=len(n["missing"])+len(n["extra"])+len(n["mismatched"])
    return CorpusResult(case.id,mf==0 and nf==0,mf,nf,())
