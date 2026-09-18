from .thresholds import fidelity_status
def fidelity_report_dict(r):return {"score":r.score,"status":fidelity_status(r),"exact":r.exact,"sections":[x.__dict__ for x in r.sections]}
