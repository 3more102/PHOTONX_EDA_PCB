SOURCE_KINDS=("oscillator","crystal","clock_generator","pll")
def source_score(source_kind):
    return .25 if str(source_kind).lower() in SOURCE_KINDS else 0.0
