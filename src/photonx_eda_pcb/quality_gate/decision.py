from .model import GateResult
from .checks import issue_count_findings,metric_min_finding
from .regression_gate import regression_findings
from .provenance_gate import provenance_findings

def evaluate_gate(counts,metrics,thresholds,regression_failures=0):
    findings=[];findings.extend(issue_count_findings(counts,thresholds));findings.extend(regression_findings(regression_failures,thresholds))
    if 'provenance_coverage' in metrics:findings.extend(provenance_findings(metrics['provenance_coverage'],thresholds))
    if 'completeness' in metrics:
        f=metric_min_finding('completeness',metrics['completeness'],thresholds.min_completeness)
        if f:findings.append(f)
    return GateResult(not any(x.severity=='error' for x in findings),findings,dict(metrics))
