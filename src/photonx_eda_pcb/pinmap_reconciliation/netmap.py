def reconcile_pin_nets(expected,observed):
    issues=[]
    for pin in sorted(set(expected)|set(observed)):
        if pin not in expected:issues.append((pin,"UNEXPECTED_NET",None,observed[pin]))
        elif pin not in observed:issues.append((pin,"MISSING_NET",expected[pin],None))
        elif expected[pin]!=observed[pin]:issues.append((pin,"NET_MISMATCH",expected[pin],observed[pin]))
    return issues
