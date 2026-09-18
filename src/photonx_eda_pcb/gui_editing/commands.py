from photonx_eda_pcb.command_bus.model import Command
def edit_to_command(op):return Command("edit."+op.kind,{"id":op.id,"object_id":op.object_id,"before":op.before,"after":op.after,"reason":op.reason},"gui")
