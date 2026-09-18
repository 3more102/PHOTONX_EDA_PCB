from .model import ExportResult
from .plan import export_plan
def run_exports(requests,registry,context=None,continue_on_error=True):
    out=[]
    for r in export_plan(requests):
        try:out.append(ExportResult(r.id,True,registry.get(r.format)(context,r.options),""))
        except Exception as exc:
            out.append(ExportResult(r.id,False,None,f"{type(exc).__name__}: {exc}"))
            if not continue_on_error:break
    return out
