def validate_job(job):
    issues=[]
    if not job.id.strip():issues.append("BATCH_JOB_ID_EMPTY")
    if not job.command.strip():issues.append("BATCH_COMMAND_EMPTY")
    if len(job.inputs)!=len(set(job.inputs)):issues.append("BATCH_DUPLICATE_INPUT")
    return issues
