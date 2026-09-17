import re

def classify_token(token):
    t=token.text.strip().upper()
    if re.fullmatch(r'R\d+',t):return 'reference_resistor'
    if re.fullmatch(r'C\d+',t):return 'reference_capacitor'
    if re.fullmatch(r'(U|IC)\d+',t):return 'reference_ic'
    if re.fullmatch(r'D\d+',t):return 'reference_diode'
    if re.fullmatch(r'J\d+',t):return 'reference_connector'
    if t in {'GND','VCC','VIN','VOUT','3V3','5V','12V'}:return 'net_label_candidate'
    return 'unknown'
