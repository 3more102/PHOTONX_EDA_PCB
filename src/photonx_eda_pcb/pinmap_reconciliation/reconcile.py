from .model import PinMapIssue,PinMapReport
from .normalize import norm_pin,norm_name
def reconcile_pinmap(component_id,expected_pins,observed_pins):
    exp={norm_pin(k):norm_name(v) for k,v in expected_pins.items()}
    obs={norm_pin(k):norm_name(v) for k,v in observed_pins.items()}
    issues=[];matched=0
    for pin in sorted(set(exp)|set(obs)):
        if pin not in exp:issues.append(PinMapIssue("UNEXPECTED_PIN",pin,"",obs[pin]));continue
        if pin not in obs:issues.append(PinMapIssue("MISSING_PIN",pin,exp[pin],""));continue
        if exp[pin] and obs[pin] and exp[pin]!=obs[pin]:issues.append(PinMapIssue("PIN_NAME_MISMATCH",pin,exp[pin],obs[pin]))
        else:matched+=1
    return PinMapReport(str(component_id),issues,matched,len(set(exp)|set(obs)))
