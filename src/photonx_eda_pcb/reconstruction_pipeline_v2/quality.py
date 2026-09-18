def quality_score(context):
    errors=sum(1 for d in context.diagnostics if "ERROR" in d or "MISSING" in d)
    produced=len(context.artifacts)
    return round(max(0.0,min(1.0,(produced/(produced+errors+1 if produced+errors+1 else 1)))),6)
