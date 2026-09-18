def profile_confidence(profile):
    if not profile.rules:return 0.0
    return round(sum(r.confidence for r in profile.rules.values())/len(profile.rules),6)
