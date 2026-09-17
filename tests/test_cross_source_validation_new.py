from photonx_eda_pcb.cross_source_validation.model import SourceObservation
from photonx_eda_pcb.cross_source_validation.merge import merge_observations
from photonx_eda_pcb.cross_source_validation.conflicts import find_conflicts

def test_cross_source_merge_and_conflict():
    x=[SourceObservation('silkscreen','N1','label','GND',.5),SourceObservation('ipc356','N1','label','0V',1.0)]
    assert merge_observations(x)[('N1','label')]['value']=='0V'
    assert len(find_conflicts(x))==1
