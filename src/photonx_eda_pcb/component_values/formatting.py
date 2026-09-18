def format_resistance(ohms):
    v=float(ohms)
    if v>=1e6:return f"{v/1e6:g}MΩ"
    if v>=1e3:return f"{v/1e3:g}kΩ"
    return f"{v:g}Ω"
def format_capacitance(farads):
    v=float(farads)
    if v>=1e-6:return f"{v/1e-6:g}µF"
    if v>=1e-9:return f"{v/1e-9:g}nF"
    return f"{v/1e-12:g}pF"
