from .metrics import consistency_metrics
def consistency_report_dict(r):
    return {"metrics":consistency_metrics(r),"findings":[x.__dict__ for x in r.findings],"consensus":[{"subject_id":k[0],"field":k[1],**v} for k,v in sorted(r.consensus.items())]}
