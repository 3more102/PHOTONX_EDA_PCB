from photonx_eda_pcb.plugin_api.hooks import HookRegistry
def test_hooks_emit():
    h=HookRegistry();h.subscribe("x",lambda v:v+1);h.subscribe("x",lambda v:v*2)
    assert h.emit("x",3)==[4,6]
