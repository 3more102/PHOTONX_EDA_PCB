class HookRegistry:
    def __init__(self):self._hooks={}
    def subscribe(self,name,callback):
        self._hooks.setdefault(str(name),[]).append(callback)
    def emit(self,name,*args,**kwargs):
        return [fn(*args,**kwargs) for fn in list(self._hooks.get(str(name),[]))]
