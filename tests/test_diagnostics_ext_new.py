from photonx_eda_pcb.diagnostics_ext.catalog import message_for
from photonx_eda_pcb.diagnostics_ext.policy import at_least
def test_diagnostic_helpers():
    assert "arc" in message_for("GERBER_ARC_INVALID").lower()
    assert "x2" in message_for("X2_DRILL_SPAN_UNRESOLVED").lower()
    assert at_least("error","warning")
