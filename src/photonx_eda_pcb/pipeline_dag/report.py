def run_summary(result):
    return {"executed":list(result.executed),"skipped":list(result.skipped),"failed":[{"node":n,"error":e} for n,e in result.failed],"artifact_count":len(result.artifacts),"success":not result.failed}
