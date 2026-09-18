def analysis_summary(a):
    return {"fingerprints":len(a.fingerprints),"repeated_groups":len(a.repeated_groups),"channels":len(a.channels),"pattern_matches":len(a.pattern_matches),"evidence_records":len(a.evidence_records),"review_items":len(a.review_items)}
