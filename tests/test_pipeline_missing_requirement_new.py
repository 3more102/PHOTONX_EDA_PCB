from photonx_eda_pcb.pipeline_stages.context import PipelineContext
from photonx_eda_pcb.pipeline_stages.stage import Stage,StageResult
from photonx_eda_pcb.pipeline_stages.runner import run_pipeline

def test_missing_requirement_stops_pipeline():
    ctx=PipelineContext();s=Stage('x',lambda c:StageResult('x',True),requires=('missing',))
    out=run_pipeline(ctx,[s])
    assert out==[('x',False)]
    assert ctx.diagnostics[0]['code']=='PIPELINE_REQUIREMENT_MISSING'
