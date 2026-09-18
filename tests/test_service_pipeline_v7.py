from photonx_eda_pcb.service_facade.pipeline_service import PipelineService
from photonx_eda_pcb.pipeline_dag import DagNode,PipelineDag
def test_pipeline_service():
    d=PipelineDag().add(DagNode("x",lambda i:{"x":1},(),("x",)))
    assert PipelineService().execute(d).artifacts["x"]==1
