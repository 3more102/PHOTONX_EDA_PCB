from photonx_eda_pcb.command_bus import Command,CommandRegistry,CommandBus
def test_command_bus_executes():
    r=CommandRegistry();r.register("add",lambda p,c:p["a"]+p["b"])
    b=CommandBus(r)
    assert b.execute(Command("add",{"a":2,"b":3}))==5
    assert len(b.history)==1
