def change_report(cs):
    return [{"path":c.path,"type":c.change_type,"before_sha":c.before.sha256 if c.before else None,"after_sha":c.after.sha256 if c.after else None} for c in cs.changes]
