def validate_symbol(e):
    issues=[]
    if not e.name:issues.append("SYMBOL_NAME_EMPTY")
    nums=[p.number for p in e.pins]
    if not nums:issues.append("SYMBOL_NO_PINS")
    if len(nums)!=len(set(nums)):issues.append("SYMBOL_DUPLICATE_PIN")
    return issues
