LOW_TOKENS=("/RESET","RESET_N","RESET#","NRST","NRESET","RST_N","POR_N")
HIGH_TOKENS=("RESET","RST","POR","PWRGOOD_RESET")
def reset_label(label):
    s=str(label or "").upper().replace(" ","")
    if any(t in s for t in LOW_TOKENS):return True,.8,("active_low_label",)
    if any(t in s for t in HIGH_TOKENS):return False,.7,("reset_label",)
    return None,0.0,()
