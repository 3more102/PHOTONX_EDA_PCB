from photonx_eda_pcb.symbol_catalog.catalog import SymbolCatalog
from photonx_eda_pcb.symbol_catalog.defaults import common_symbols
from photonx_eda_pcb.symbol_catalog import match_symbol,validate_symbol
def test_symbol_match():
    c=SymbolCatalog(common_symbols())
    m=match_symbol(c,kind="resistor",pin_count=2,reference_prefix="R")
    assert m[0][1].name=="Device:R" and m[0][0]==1.0
    assert validate_symbol(m[0][1])==[]
