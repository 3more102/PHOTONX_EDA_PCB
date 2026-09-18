class CommandController:
    def __init__(self,bus):self.bus=bus
    def execute(self,command,context=None):return self.bus.execute(command,context)
    def history(self):return list(self.bus.history)
