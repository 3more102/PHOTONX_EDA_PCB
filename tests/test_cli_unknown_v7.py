from photonx_eda_pcb.cli_facade import CliRouter
from photonx_eda_pcb.cli_facade.model import CliRequest
def test_unknown_cli_command():
    r=CliRouter().dispatch(CliRequest("missing"))
    assert not r.success and r.exit_code==2
