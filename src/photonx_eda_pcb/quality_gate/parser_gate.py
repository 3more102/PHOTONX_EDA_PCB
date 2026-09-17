from .model import GateFinding
def parser_findings(diagnostics):
    silent=[x for x in diagnostics if (getattr(x,'code',None) or (x.get('code') if isinstance(x,dict) else None))=='SILENT_DROP']
    return [GateFinding('error','GATE_SILENT_PARSE_DROP','parser reported silent data loss',len(silent),0)] if silent else []
