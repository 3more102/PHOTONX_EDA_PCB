from photonx_eda_pcb.incremental_pipeline import StageSpec
from photonx_eda_pcb.incremental_pipeline.planner import plan_recompute
def test_recompute_propagates_downstream():
    s=[StageSpec("parse"),StageSpec("geometry",("parse",)),StageSpec("nets",("geometry",)),StageSpec("report",("nets",))]
    assert plan_recompute(s,["geometry"])==["geometry","nets","report"]
