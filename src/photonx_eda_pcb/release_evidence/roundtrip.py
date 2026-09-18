def roundtrip_passed(results):
    items=list(results)
    return bool(items) and all(getattr(x,"equal",getattr(x,"passed",False)) for x in items)
