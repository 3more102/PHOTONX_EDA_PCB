def validate_review_item(item):
    issues=[]
    if not 0<=item.confidence<=1: issues.append(("error","REVIEW_CONFIDENCE_RANGE",item.id))
    if item.status not in {"open","resolved"}: issues.append(("error","REVIEW_STATUS_INVALID",item.id,item.status))
    return issues
