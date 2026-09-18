from photonx_eda_pcb.diagnostic_catalog import default_catalog
from photonx_eda_pcb.diagnostic_catalog.render import render_diagnostic
def test_render_diagnostic():
    d=render_diagnostic(default_catalog().get("LOW_CONFIDENCE"),{"id":"U1"})
    assert d["context"]["id"]=="U1"
