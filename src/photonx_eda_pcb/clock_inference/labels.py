CLOCK_TOKENS=("CLK","CLOCK","MCLK","BCLK","PCLK","REFCLK","SYSCLK","XTAL","OSC")
def label_clock_score(label):
    s=str(label or "").upper()
    hits=[t for t in CLOCK_TOKENS if t in s]
    return (0.7 if hits else 0.0,tuple("label:"+x for x in hits))
