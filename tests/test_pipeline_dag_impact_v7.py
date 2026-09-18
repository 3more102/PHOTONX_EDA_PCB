from photonx_eda_pcb.pipeline_dag import DagNode,PipelineDag
from photonx_eda_pcb.pipeline_dag.impact import impacted_nodes
def test_impacted_nodes():
    d=PipelineDag().add(DagNode("a",lambda i:{"x":1},(),("x",))).add(DagNode("b",lambda i:{"y":1},("x",),("y",))).add(DagNode("c",lambda i:{"z":1},("y",),("z",)))
    assert impacted_nodes(d,["a"])==["a","b","c"]
