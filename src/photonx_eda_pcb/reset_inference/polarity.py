def polarity_label(candidate):
    if candidate.active_low is True:return "active_low"
    if candidate.active_low is False:return "active_high"
    return "unknown"
