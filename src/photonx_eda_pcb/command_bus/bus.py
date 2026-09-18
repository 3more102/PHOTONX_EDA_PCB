class CommandBus:
    def __init__(self,registry):self.registry=registry;self.history=[];self.failures=[]
    def execute(self,command,context=None):
        try:
            value=self.registry.get(command.name)(command.payload,context)
            self.history.append(command)
            return value
        except Exception as exc:
            self.failures.append((command.name,type(exc).__name__,str(exc)))
            raise
