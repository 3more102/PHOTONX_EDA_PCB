from .model import SymbolEntry,SymbolPin
def common_symbols():
    return [SymbolEntry("Device:R","resistor",(SymbolPin("1"),SymbolPin("2")),"R"),SymbolEntry("Device:C","capacitor",(SymbolPin("1"),SymbolPin("2")),"C"),SymbolEntry("Device:LED","led",(SymbolPin("1","K"),SymbolPin("2","A")),"D"),SymbolEntry("Connector_Generic:Conn_01x02","connector",(SymbolPin("1"),SymbolPin("2")),"J")]
