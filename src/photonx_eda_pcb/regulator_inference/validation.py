def validate_regulator(r):
    issues=[]
    if not 0<=r.confidence<=1:issues.append("REGULATOR_CONFIDENCE_RANGE")
    if set(r.input_nets)&set(r.output_nets):issues.append("REGULATOR_INPUT_OUTPUT_OVERLAP")
    return issues
