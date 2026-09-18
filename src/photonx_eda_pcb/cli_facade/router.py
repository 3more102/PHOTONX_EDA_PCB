from .model import CliResponse
class CliRouter:
    def __init__(self):self._handlers={}
    def register(self,name,handler):
        if name in self._handlers:raise ValueError(f"duplicate cli command: {name}")
        self._handlers[str(name)]=handler
    def commands(self):return sorted(self._handlers)
    def dispatch(self,request,context=None):
        if request.command not in self._handlers:return CliResponse(False,None,f"unknown command: {request.command}",2)
        try:return CliResponse(True,self._handlers[request.command](request,context),"",0)
        except Exception as exc:return CliResponse(False,None,f"{type(exc).__name__}: {exc}",1)
