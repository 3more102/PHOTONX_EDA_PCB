from photonx_eda_pcb.batch_cli.model import BatchJob
from photonx_eda_pcb.batch_cli.dependencies import order_jobs
def test_dependency_order():
    jobs=[BatchJob("b","x"),BatchJob("a","x")]
    assert [j.id for j in order_jobs(jobs,{"b":["a"]})]==["a","b"]
