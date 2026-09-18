def assert_within_limits(result,limits,item_count=None):
    issues=[]
    if result["max_s"]>limits.max_seconds:issues.append("STRESS_TIME_LIMIT")
    if item_count is not None and item_count>limits.max_items:issues.append("STRESS_ITEM_LIMIT")
    return issues
