def render_diagnostic(definition,context=None):
    return {"code":definition.code,"severity":definition.severity,"title":definition.title,"description":definition.description,"remediation":definition.remediation,"context":dict(context or {})}
