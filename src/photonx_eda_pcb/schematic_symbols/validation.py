def validate_symbol(s):
    issues=[]
    if not s.library_id:issues.append("SYMBOL_LIBRARY_ID_EMPTY")
    nums=[p.number for p in s.pins]
    if len(nums)!=len(set(nums)):issues.append("SYMBOL_DUPLICATE_PIN_NUMBER")
    if not 0<=s.confidence<=1:issues.append("SYMBOL_CONFIDENCE_RANGE")
    return issues
