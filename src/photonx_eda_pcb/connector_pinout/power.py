def power_pins(pinout):return [p for p in pinout.pins if p.role=="power"]
def ground_pins(pinout):return [p for p in pinout.pins if p.role=="ground"]
