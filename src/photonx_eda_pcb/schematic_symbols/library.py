class SymbolLibrary:
    def __init__(self):self._rules={}
    def register(self,kind,library_id,pin_count=None):
        self._rules[str(kind).lower()]={"library_id":library_id,"pin_count":pin_count}
    def lookup(self,kind,pin_count=None):
        r=self._rules.get(str(kind).lower())
        if not r:return None
        if r["pin_count"] is not None and pin_count is not None and int(pin_count)!=int(r["pin_count"]):return None
        return r["library_id"]
def default_library():
    lib=SymbolLibrary()
    lib.register("resistor","Device:R",2);lib.register("capacitor","Device:C",2)
    lib.register("led","Device:LED",2);lib.register("diode","Device:D",2)
    lib.register("inductor","Device:L",2)
    return lib
