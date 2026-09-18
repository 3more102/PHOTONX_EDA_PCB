def add_analysis_evidence(database,analysis):
    added=[]
    for r in analysis.evidence_records:
        database.upsert(r);added.append(r.id)
    return added
