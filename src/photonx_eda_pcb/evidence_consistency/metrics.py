def consistency_metrics(report):
    total=len(report.consensus);conflicts=sum(x.code=="EVIDENCE_CONFLICT" for x in report.findings)
    errors=sum(x.severity=="error" for x in report.findings)
    return {"claims":total,"conflicts":conflicts,"errors":errors,"conflict_rate":0.0 if not total else round(conflicts/total,6)}
