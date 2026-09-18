DEFAULT_PERMISSIONS={"filesystem_read":False,"filesystem_write":False,"network":False,"subprocess":False}
def normalized_permissions(values=None):
    out=dict(DEFAULT_PERMISSIONS);out.update(values or {});return {k:bool(v) for k,v in out.items()}
