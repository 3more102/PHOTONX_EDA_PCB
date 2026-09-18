from .model import ValidationResult,ValidationReport
def run_validation(registry,context=None,groups=None):
    want=set(groups or []);out=[]
    for check,fn in registry.items():
        if want and check.group not in want:continue
        try:
            value=fn(context)
            msgs=tuple(value if isinstance(value,(list,tuple)) else (() if value in (None,True) else (str(value),)))
            passed=not msgs
        except Exception as exc:
            passed=False;msgs=(f"{type(exc).__name__}: {exc}",)
        out.append(ValidationResult(check.name,passed,check.severity,msgs))
    return ValidationReport(out)
