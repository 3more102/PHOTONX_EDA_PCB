from dataclasses import dataclass
@dataclass(frozen=True)
class StackupIssue: severity:str; code:str; message:str

def validate_stackup(stackup):
    issues=[]; names=[x.name for x in stackup.layers]; orders=[x.order for x in stackup.layers]
    if len(names)!=len(set(names)):issues.append(StackupIssue('error','STACKUP_DUPLICATE_LAYER','duplicate layer name'))
    if len(orders)!=len(set(orders)):issues.append(StackupIssue('error','STACKUP_DUPLICATE_ORDER','duplicate layer order'))
    if not stackup.copper_layers():issues.append(StackupIssue('warning','STACKUP_NO_COPPER','no copper layers inferred'))
    if not 0<=stackup.confidence<=1:issues.append(StackupIssue('error','STACKUP_CONFIDENCE','confidence outside [0,1]'))
    return issues
