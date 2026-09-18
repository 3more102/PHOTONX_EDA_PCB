from photonx_eda_pcb.pipeline_dag import DagNode,PipelineDag,execute_dag,validate_dag
def test_pipeline_dag_executes_in_dependency_order():
    d=PipelineDag().add(DagNode("parse",lambda i:{"parsed":"x"},(),("parsed",))).add(DagNode("geom",lambda i:{"geom":i["parsed"]+"g"},("parsed",),("geom",)))
    r=execute_dag(d)
    assert r.executed==["parse","geom"]
    assert r.artifacts["geom"]=="xg"
    assert validate_dag(d)==[]
