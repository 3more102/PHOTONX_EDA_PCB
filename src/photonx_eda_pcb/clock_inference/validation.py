def validate_clock(c):
    issues=[]
    if not 0<=c.confidence<=1:issues.append("CLOCK_CONFIDENCE_RANGE")
    if c.fanout<0:issues.append("CLOCK_NEGATIVE_FANOUT")
    if c.frequency_hz is not None and c.frequency_hz<=0:issues.append("CLOCK_BAD_FREQUENCY")
    return issues
