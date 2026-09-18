def decode_capacitor_code(text):
    s=str(text).strip().upper()
    if s.isdigit() and len(s)==3:
        pf=int(s[:2])*(10**int(s[2]))
        return pf*1e-12
    return None
