from .model import ConsistencyFinding,ConsistencyReport
from .consensus import consensus_for
def analyze_consistency(items,ambiguity_margin=.1):
    grouped={}
    for x in items:grouped.setdefault((x.subject_id,x.field),[]).append(x)
    report=ConsistencyReport()
    for key,obs in sorted(grouped.items()):
        ranked=consensus_for(obs)
        if not ranked:continue
        best=ranked[0];report.consensus[key]={"value_repr":best[1],"confidence":round(best[0],12),"groups":sorted(best[2])}
        if len(ranked)>1:
            delta=best[0]-ranked[1][0]
            sev="error" if delta<=float(ambiguity_margin) and ranked[1][0]>=.5 else "warning"
            report.findings.append(ConsistencyFinding("EVIDENCE_CONFLICT",sev,key[0],key[1],f"top claims differ by confidence margin {delta:.6f}"))
        if best[0]<.5:
            report.findings.append(ConsistencyFinding("EVIDENCE_WEAK_CONSENSUS","warning",key[0],key[1],f"consensus confidence {best[0]:.6f}"))
    return report
