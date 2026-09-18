def validate_power_architecture(a):
    issues=[]
    if not 0<=a.confidence<=1:issues.append("POWER_ARCH_CONFIDENCE_RANGE")
    for s in a.stages:
        if set(s.input_rails)&set(s.output_rails):issues.append("POWER_ARCH_STAGE_RAIL_OVERLAP")
    return issues
