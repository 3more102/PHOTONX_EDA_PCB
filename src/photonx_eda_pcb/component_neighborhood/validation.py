def validate_neighborhood(n):
    issues=[]
    if n.degree!=len(n.neighbors):issues.append("NEIGHBORHOOD_DEGREE_MISMATCH")
    if len(n.neighbors)!=len(set(n.neighbors)):issues.append("NEIGHBORHOOD_DUPLICATE_NEIGHBOR")
    return issues
