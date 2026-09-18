SWD={"SWDIO","SWCLK"};JTAG={"TCK","TMS","TDI","TDO"};EXTRA_RESET={"NRST","RESET_N","NTRST","TRST"}
def debug_signal(label):
    s=str(label or "").upper().replace(" ","").replace("/","")
    if any(x in s for x in SWD):
        return "SWD",next(x for x in SWD if x in s)
    if any(x in s for x in JTAG):
        return "JTAG",next(x for x in JTAG if x in s)
    if any(x in s for x in EXTRA_RESET):return "RESET","RESET"
    return None
