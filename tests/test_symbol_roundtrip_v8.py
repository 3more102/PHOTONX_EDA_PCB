from photonx_eda_pcb.symbol_catalog.catalog import SymbolCatalog
from photonx_eda_pcb.symbol_catalog.defaults import common_symbols
from photonx_eda_pcb.symbol_catalog.serialize import dumps_catalog,loads_catalog
def test_symbol_roundtrip():
    c=SymbolCatalog(common_symbols());d=loads_catalog(dumps_catalog(c))
    assert [x.name for x in d.all()]==[x.name for x in c.all()]
