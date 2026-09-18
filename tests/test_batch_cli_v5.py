from photonx_eda_pcb.batch_cli import BatchJob,run_batch,validate_job
from photonx_eda_pcb.batch_cli.registry import BatchCommandRegistry
from photonx_eda_pcb.batch_cli.summary import summarize_results
def test_batch_runner():
    r=BatchCommandRegistry();r.register("echo",lambda job,ctx:list(job.inputs))
    jobs=[BatchJob("j1","echo",("a","b"))]
    out=run_batch(jobs,r)
    assert out[0].success and out[0].output==["a","b"] and validate_job(jobs[0])==[]
    assert summarize_results(out)["success"]
