from photonx_eda_pcb.search_presets.model import SearchPreset
from photonx_eda_pcb.search_presets import apply_preset,validate_preset
def test_search_preset():
    p=SearchPreset("low","confidence<0.7","all","confidence")
    out=apply_preset([{"id":"a","confidence":.9},{"id":"b","confidence":.4}],p)
    assert [x["id"] for x in out]==["b"] and validate_preset(p)==[]
