def checkpoint_status(c):
    if c.closed:return "closed"
    if any(d.decision=="rejected" for d in c.decisions):return "blocked"
    if any(d.decision=="needs_work" for d in c.decisions):return "needs_work"
    if c.decisions:return "reviewed"
    return "open"
