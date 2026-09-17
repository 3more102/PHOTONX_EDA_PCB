from .model import GateFinding
def drc_findings(issues):
    errors=sum((getattr(x,'severity',None) or (x.get('severity') if isinstance(x,dict) else None))=='error' for x in issues)
    return [] if errors==0 else [GateFinding('error','GATE_DRC_ERRORS','DRC errors present',errors,0)]
