from photonx_eda_pcb.reporting_bridge import build_unified_report
from photonx_eda_pcb.reporting_bridge.json_report import unified_json
def test_unified_report_deterministic_sections():
    r=build_unified_report("X",{"z":{"b":2},"a":{"a":1}})
    assert [x.name for x in r.sections]==["a","z"]
    assert '"title":"X"' in unified_json(r)
