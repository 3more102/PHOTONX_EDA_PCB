from .model import GateFinding
def issue_count_findings(counts,t):
    out=[]
    if counts.get('error',0)>t.max_errors:out.append(GateFinding('error','GATE_ERROR_COUNT','too many errors',counts.get('error',0),t.max_errors))
    if counts.get('warning',0)>t.max_warnings:out.append(GateFinding('warning','GATE_WARNING_COUNT','too many warnings',counts.get('warning',0),t.max_warnings))
    return out
def metric_min_finding(name,value,minimum):return None if value>=minimum else GateFinding('error',f'GATE_{name.upper()}_LOW',f'{name} below minimum',value,minimum)
