from .model import SymbolHypothesis
from .library import default_library
from .pins import named_two_pin,generic_pins
def infer_symbol(component_id,kind,pin_count,library=None):
    lib=library or default_library();lid=lib.lookup(kind,pin_count)
    if lid:
        pins=named_two_pin(kind) if int(pin_count)==2 else generic_pins(pin_count)
        return SymbolHypothesis(str(component_id),lid,.75,pins,["component_kind","pin_count"])
    return SymbolHypothesis(str(component_id),"Device:Unknown",.2,generic_pins(pin_count),["pin_count_only"])
