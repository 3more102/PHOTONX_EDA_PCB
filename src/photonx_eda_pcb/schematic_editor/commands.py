from photonx_eda_pcb.command_bus.model import Command
def move_command(symbol_id,before,after):return Command("schematic.move_symbol",{"symbol_id":str(symbol_id),"before":tuple(before),"after":tuple(after)},"schematic_editor")
def property_command(symbol_id,name,before,after):return Command("schematic.set_property",{"symbol_id":str(symbol_id),"name":str(name),"before":before,"after":after},"schematic_editor")
