from photonx_eda_pcb.pipeline_dag import DagNode,PipelineDag,execute_dag
from photonx_eda_pcb.incremental_cache.store import IncrementalCache
def test_pipeline_dag_uses_cache():
    calls={"n":0}
    def fn(i):calls["n"]+=1;return {"x":1}
    d=PipelineDag().add(DagNode("a",fn,(),("x",)))
    c=IncrementalCache()
    execute_dag(d,cache=c);execute_dag(d,cache=c)
    assert calls["n"]==1
