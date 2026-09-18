class ServiceContainer:
    def __init__(self):self._services={}
    def register(self,name,service):
        if name in self._services:raise ValueError(f"service exists: {name}")
        self._services[str(name)]=service;return service
    def get(self,name):return self._services[str(name)]
    def names(self):return sorted(self._services)
