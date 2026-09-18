PROTECTED_KEYS={"name","artifacts"}
def protected_keys_preserved(before,after):
    return all(k not in before or k in after for k in PROTECTED_KEYS)
