from photonx_eda_pcb.command_bus.model import Command
from photonx_eda_pcb.command_bus.serialization import dump_command,load_command
def test_command_roundtrip():
    c=Command("x",{"a":1},"test")
    assert load_command(dump_command(c))==c
