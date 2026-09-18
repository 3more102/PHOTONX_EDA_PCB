def validate_analog_block(b):
    issues=[]
    if not b.components:issues.append("ANALOG_BLOCK_EMPTY")
    if not 0<=b.confidence<=1:issues.append("ANALOG_BLOCK_CONFIDENCE_RANGE")
    if len(b.components)!=len(set(b.components)):issues.append("ANALOG_BLOCK_DUPLICATE_COMPONENT")
    return issues
