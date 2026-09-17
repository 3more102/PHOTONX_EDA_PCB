VALID_DECISIONS={"accept","reject","edit","defer"}
def apply_decision(item,decision):
    if decision not in VALID_DECISIONS: raise ValueError(f"invalid review decision: {decision}")
    item.decision=decision; item.status="open" if decision=="defer" else "resolved"; return item
