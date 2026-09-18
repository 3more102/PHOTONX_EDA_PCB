from photonx_eda_pcb.cli_facade import CliRouter,register_default_handlers
from photonx_eda_pcb.cli_facade.parse import parse_argv
def test_cli_facade_echo():
    r=register_default_handlers(CliRouter())
    q=parse_argv(["echo","a","--mode","fast","--flag"])
    out=r.dispatch(q)
    assert out.success and out.data["args"]==["a"] and out.data["options"]=={"mode":"fast","flag":True}
