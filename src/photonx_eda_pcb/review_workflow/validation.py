VALID_STATUS={"open","closed","deferred"};VALID_DECISION={"","accepted","rejected","deferred"}
def validate_queue(queue):
    issues=[];ids=set()
    for x in queue.items:
        if x.id in ids:issues.append("REVIEW_DUPLICATE_ID")
        ids.add(x.id)
        if x.status not in VALID_STATUS:issues.append("REVIEW_BAD_STATUS")
        if x.decision not in VALID_DECISION:issues.append("REVIEW_BAD_DECISION")
    return issues
