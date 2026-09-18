class PluginRegistry:
    def __init__(self):self._plugins={}
    def register(self,plugin):
        meta=getattr(plugin,"metadata",None)
        if meta is None:raise ValueError("plugin metadata required")
        if meta.name in self._plugins:raise ValueError(f"duplicate plugin: {meta.name}")
        self._plugins[meta.name]=plugin
    def get(self,name):return self._plugins[name]
    def names(self):return sorted(self._plugins)
    def plugins(self):return [self._plugins[n] for n in self.names()]
