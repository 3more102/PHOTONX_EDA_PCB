from .model import HealthMetric
def from_status(*,tests=True,unsupported=0,validation_score=1.0,provenance_score=1.0,determinism=True):
    return [HealthMetric("tests",1.0 if tests else 0.0,2),HealthMetric("unsupported_syntax",1.0 if int(unsupported)==0 else 0.0,3,str(unsupported)),HealthMetric("validation",float(validation_score),3),HealthMetric("provenance",float(provenance_score),2),HealthMetric("determinism",1.0 if determinism else 0.0,1)]
