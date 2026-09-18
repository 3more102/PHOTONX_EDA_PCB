from .coverage import pinmap_coverage
def pinmap_report(r):return {"component_id":r.component_id,"matched":r.matched,"total":r.total,"coverage":pinmap_coverage(r),"issues":[x.__dict__ for x in r.issues]}
