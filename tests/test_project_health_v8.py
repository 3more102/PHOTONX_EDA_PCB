from photonx_eda_pcb.project_health.default_metrics import from_status
from photonx_eda_pcb.project_health import compute_health,health_grade
def test_project_health_good():
    h=compute_health(from_status(tests=True,unsupported=0,validation_score=1,provenance_score=1,determinism=True))
    assert h.score==1.0 and health_grade(h.score)=="A"
def test_project_health_degrades():
    h=compute_health(from_status(tests=True,unsupported=3,validation_score=.5,provenance_score=.7,determinism=True))
    assert h.score<.8
