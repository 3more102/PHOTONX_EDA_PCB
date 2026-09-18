from .model import ValueHypothesis
from .resistor_codes import decode_resistor_marking
from .capacitor_codes import decode_capacitor_code
from .formatting import format_resistance,format_capacitance
def infer_value(component_id,marking,kind):
    k=str(kind).lower()
    if "res" in k:
        v=decode_resistor_marking(marking)
        return ValueHypothesis(str(component_id),None if v is None else format_resistance(v),0.8 if v is not None else 0.0,("marking",) if v is not None else ())
    if "cap" in k:
        v=decode_capacitor_code(marking)
        return ValueHypothesis(str(component_id),None if v is None else format_capacitance(v),0.7 if v is not None else 0.0,("marking",) if v is not None else ())
    return ValueHypothesis(str(component_id),None,0.0,())
