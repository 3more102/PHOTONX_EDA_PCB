def labeled_pin_fraction(pinout):
    return 1.0 if not pinout.pins else round(sum(p.confidence>.4 for p in pinout.pins)/len(pinout.pins),6)
