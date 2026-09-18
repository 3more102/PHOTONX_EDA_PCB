def validate_package_assessment(a):
    issues=[]
    if any(v<0 for v in a.present.values()):issues.append("PACKAGE_NEGATIVE_COUNT")
    return issues
