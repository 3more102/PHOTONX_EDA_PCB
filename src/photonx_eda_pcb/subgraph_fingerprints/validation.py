def validate_fingerprint(f):
    issues=[]
    if f.radius<0:issues.append("FINGERPRINT_NEGATIVE_RADIUS")
    if not f.nodes:issues.append("FINGERPRINT_EMPTY")
    if not f.topology_hash:issues.append("FINGERPRINT_TOPOLOGY_HASH_EMPTY")
    if not 0<=f.confidence<=1:issues.append("FINGERPRINT_CONFIDENCE_RANGE")
    return issues
