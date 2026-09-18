def validate_block(b):
    issues=[]
    if not b.components:issues.append("BLOCK_EMPTY_COMPONENTS")
    if not 0<=b.confidence<=1:issues.append("BLOCK_CONFIDENCE_RANGE")
    return issues
