from photonx_eda_pcb.import_orchestrator import ImportRequest,import_many
from photonx_eda_pcb.import_orchestrator.summary import import_summary
from photonx_eda_pcb.source_adapters.defaults import default_adapters
def test_import_many_summary():
    rs=import_many([ImportRequest("a.json","{}"),ImportRequest("b.json","[]")],default_adapters())
    assert import_summary(rs)["passed"]==2
