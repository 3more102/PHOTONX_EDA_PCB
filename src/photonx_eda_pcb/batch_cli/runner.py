from .model import BatchResult
def run_batch(jobs,registry,context=None,stop_on_error=False):
    results=[]
    for job in jobs:
        try:
            out=registry.get(job.command)(job,context)
            results.append(BatchResult(job.id,True,out,""))
        except Exception as exc:
            results.append(BatchResult(job.id,False,None,f"{type(exc).__name__}: {exc}"))
            if stop_on_error:break
    return results
