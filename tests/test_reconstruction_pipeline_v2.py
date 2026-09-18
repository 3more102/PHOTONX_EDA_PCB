from photonx_eda_pcb.reconstruction_pipeline_v2.context import ReconstructionContext
from photonx_eda_pcb.reconstruction_pipeline_v2.stage import Stage
from photonx_eda_pcb.reconstruction_pipeline_v2.runner import run_pipeline
from photonx_eda_pcb.reconstruction_pipeline_v2.quality import quality_score
def test_pipeline_produces_artifacts():
    c=ReconstructionContext(inputs={"raw":"x"})
    s=[Stage("parse",lambda ctx:{"parsed":ctx.inputs["raw"]},("raw",),("parsed",)),Stage("norm",lambda ctx:{"normalized":ctx.artifacts["parsed"]},("parsed",),("normalized",))]
    run_pipeline(c,s)
    assert c.artifacts["normalized"]=="x"
    assert c.diagnostics==[]
    assert quality_score(c)>0
def test_pipeline_reports_missing_requirement():
    c=ReconstructionContext()
    run_pipeline(c,[Stage("x",lambda ctx:{"x":1},("missing",),("x",))])
    assert c.diagnostics and "STAGE_MISSING" in c.diagnostics[0]
