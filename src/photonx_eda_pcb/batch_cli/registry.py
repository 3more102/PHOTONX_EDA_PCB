class BatchCommandRegistry:
    def __init__(self):self._commands={}
    def register(self,name,fn):
        if name in self._commands:raise ValueError(f"duplicate batch command {name}")
        self._commands[str(name)]=fn
    def get(self,name):return self._commands[name]
    def names(self):return sorted(self._commands)
