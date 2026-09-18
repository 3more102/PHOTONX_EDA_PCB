from .model import SignalIntegrityRisk
from .levels import risk_level
def analyze_si_risk(net_id,*,return_path_risk=0,via_risk=0,skew_risk=0,impedance_risk=0,length_risk=0,confidence=0):
    factors={"return_path":float(return_path_risk),"via":float(via_risk),"skew":float(skew_risk),"impedance":float(impedance_risk),"length":float(length_risk)}
    weights={"return_path":.3,"via":.15,"skew":.2,"impedance":.25,"length":.1}
    score=sum(max(0,min(1,factors[k]))*weights[k] for k in factors)
    return SignalIntegrityRisk(str(net_id),round(score,6),risk_level(score),factors,round(min(1,max(0,float(confidence))),6))
