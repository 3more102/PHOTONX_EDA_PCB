from copy import deepcopy
def inject_fault(subject,fault):
    x=deepcopy(subject)
    if fault.kind=="set_attr":setattr(x,fault.target,fault.value)
    elif fault.kind=="delete_list_item":
        seq=getattr(x,fault.target);seq.pop(int(fault.value))
    elif fault.kind=="duplicate_list_item":
        seq=getattr(x,fault.target);seq.append(deepcopy(seq[int(fault.value)]))
    elif fault.kind=="clear_list":getattr(x,fault.target).clear()
    else:raise ValueError("unknown fault kind")
    return x
def run_fault_suite(subject,faults,detector,is_detected=lambda output:bool(output)):
    from .model import FaultResult
    out=[]
    for f in faults:
        mutated=inject_fault(subject,f);result=detector(mutated);out.append(FaultResult(f.id,bool(is_detected(result)),result))
    return out
