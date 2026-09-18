def parse_constraint(text):
    parts=[x.strip() for x in str(text).split(":")]
    if len(parts)<2:raise ValueError("expected NET:OHMS[:TOLERANCE[:MODE]]")
    from .model import ImpedanceConstraint
    return ImpedanceConstraint(parts[0],float(parts[1]),float(parts[2]) if len(parts)>2 and parts[2] else 10.0,parts[3] if len(parts)>3 and parts[3] else "single-ended")
