from photonx_eda_pcb.import_orchestrator import ImportRequest,import_one
from photonx_eda_pcb.source_adapters.defaults import default_adapters
def test_import_success():
    r=import_one(ImportRequest("a.json",'{"x":1}',"json"),default_adapters())
    assert r.success and r.document.content["x"]==1
def test_import_format_mismatch():
    r=import_one(ImportRequest("a.gbr","M02*","json"),default_adapters())
    assert not r.success and any(x.startswith("FORMAT_MISMATCH") for x in r.diagnostics)
