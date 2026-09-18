from photonx_eda_pcb.format_detection import detect_format
from photonx_eda_pcb.source_adapters.defaults import default_adapters
from photonx_eda_pcb.import_orchestrator import ImportRequest,import_one
from photonx_eda_pcb.package_catalog.catalog import PackageCatalog
from photonx_eda_pcb.package_catalog.defaults import common_packages
from photonx_eda_pcb.symbol_catalog.catalog import SymbolCatalog
from photonx_eda_pcb.symbol_catalog.defaults import common_symbols
from photonx_eda_pcb.project_health import compute_health
from photonx_eda_pcb.project_health.default_metrics import from_status
def test_phase8_end_to_end():
    assert detect_format("x.json","{}").format=="json"
    assert import_one(ImportRequest("x.json","{}"),default_adapters()).success
    assert len(PackageCatalog(common_packages()).all())>=5
    assert len(SymbolCatalog(common_symbols()).all())>=4
    assert compute_health(from_status()).score==1.0
