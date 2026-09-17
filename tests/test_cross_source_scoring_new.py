from photonx_eda_pcb.cross_source_validation.model import SourceObservation
from photonx_eda_pcb.cross_source_validation.scoring import weighted_confidence

def test_source_weighting():
    assert weighted_confidence(SourceObservation('ipc356','N1','label','GND',1.0))==1.0
    assert weighted_confidence(SourceObservation('geometry_inference','N1','label','GND',1.0))==0.4
