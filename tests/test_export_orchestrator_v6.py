from photonx_eda_pcb.export_orchestrator import ExportRequest,ExportRegistry,run_exports
from photonx_eda_pcb.export_orchestrator.report import export_summary
def test_export_orchestration():
    r=ExportRegistry();r.register("txt",lambda ctx,opt:"ok:"+opt.get("x",""))
    out=run_exports([ExportRequest("1","txt",{"x":"a"})],r)
    assert out[0].content=="ok:a" and export_summary(out)["passed"]==1
