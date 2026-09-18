from photonx_eda_pcb.source_adapters.defaults import default_adapters
from photonx_eda_pcb.format_detection.model import FormatGuess
def test_default_adapter_resolves():
    r=default_adapters();a=r.resolve(FormatGuess("gerber",.9,()))
    d=a.read("a.gbr","M02*")
    assert d.format=="gerber" and d.path=="a.gbr"
