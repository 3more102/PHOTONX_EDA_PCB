def function_coverage(items):
    if not items:return 0.0
    return round(sum(x.function is not None for x in items)/len(items),6)
