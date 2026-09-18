from photonx_eda_pcb.export_orchestrator.model import ExportResult
from photonx_eda_pcb.export_orchestrator.manifest import export_manifest
def test_export_manifest_hash():
    m=export_manifest([ExportResult("x",True,"abc","")])
    assert len(m[0]["sha256"])==64
