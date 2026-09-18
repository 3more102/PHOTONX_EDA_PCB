def pin_names(symbol):return {p.number:p.name for p in symbol.pins}
def electrical_types(symbol):return {p.number:p.electrical_type for p in symbol.pins}
