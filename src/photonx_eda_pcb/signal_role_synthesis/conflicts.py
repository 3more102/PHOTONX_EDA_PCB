def role_conflicts(role):
    r=set(role.roles);out=[]
    if "power" in r and "ground" in r:out.append("POWER_GROUND_CONFLICT")
    if "clock" in r and "reset" in r:out.append("CLOCK_RESET_CONFLICT")
    return out
