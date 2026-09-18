def package_completeness(assessment,requirements):
    req=[r for r in requirements if r.required]
    if not req:return 1.0
    good=sum(r.role not in assessment.missing for r in req)
    return round(good/len(req),6)
