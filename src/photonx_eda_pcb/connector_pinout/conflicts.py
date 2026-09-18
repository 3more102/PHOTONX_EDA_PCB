def role_conflicts(pinout):
    return [p.pin_id for p in pinout.pins if p.role=="power" and p.net_id is None]
