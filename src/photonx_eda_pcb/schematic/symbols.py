SYMBOL_HINTS={'TWO_PIN_THT':['R','C','L','D','LED','J'],'TWO_PAD_SMD':['R','C','L','D','LED'],'SOIC8_LIKE':['IC'],'DIP8_LIKE':['IC']}
def symbol_hints(kind): return SYMBOL_HINTS.get(kind,[])
