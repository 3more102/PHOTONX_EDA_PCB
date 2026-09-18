from photonx_eda_pcb.pattern_library.library import PatternLibrary
from photonx_eda_pcb.pattern_library.defaults import default_patterns
from photonx_eda_pcb.pattern_library.serialize import dumps_library,loads_library
def test_pattern_library_roundtrip():
    a=PatternLibrary(default_patterns());b=loads_library(dumps_library(a))
    assert [x.name for x in a.all()]==[x.name for x in b.all()]
