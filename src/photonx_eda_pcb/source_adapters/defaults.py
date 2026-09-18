from .registry import AdapterRegistry
from .text import TextAdapter
from .json_adapter import JsonAdapter
def default_adapters():
    r=AdapterRegistry()
    for f in ("gerber","excellon","ipc356","kicad_pcb","kicad_schematic","csv"):r.register(f,TextAdapter(f))
    r.register("json",JsonAdapter())
    return r
