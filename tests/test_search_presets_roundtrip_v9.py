from photonx_eda_pcb.search_presets.model import SearchPreset
from photonx_eda_pcb.search_presets.store import PresetStore
from photonx_eda_pcb.search_presets.serialize import dumps_presets,loads_presets
def test_presets_roundtrip():
    s=PresetStore();s.add(SearchPreset("x","confidence>=0.5"))
    assert loads_presets(dumps_presets(s)).all()==s.all()
