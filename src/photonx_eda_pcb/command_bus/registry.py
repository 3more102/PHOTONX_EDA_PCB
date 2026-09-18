class CommandRegistry:
    def __init__(self):self._handlers={}
    def register(self,name,handler):
        if name in self._handlers:raise ValueError(f"handler exists: {name}")
        self._handlers[str(name)]=handler
    def get(self,name):
        if name not in self._handlers:raise KeyError(name)
        return self._handlers[name]
    def names(self):return sorted(self._handlers)
