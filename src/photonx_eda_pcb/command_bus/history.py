def command_names(bus):return [c.name for c in bus.history]
def last_command(bus):return bus.history[-1] if bus.history else None
