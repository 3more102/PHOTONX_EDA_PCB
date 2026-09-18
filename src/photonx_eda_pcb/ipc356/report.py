def evidence_report(evidence,unmatched):
    return {"matched":len(evidence),"unmatched":len(unmatched),"nets":len({e.net_name for e in evidence}),"references":len({e.reference for e in evidence if e.reference})}
