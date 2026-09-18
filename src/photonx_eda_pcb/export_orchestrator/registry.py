class ExportRegistry:
    def __init__(self):self._items={}
    def register(self,fmt,fn):
        if fmt in self._items:raise ValueError(f"duplicate exporter: {fmt}")
        self._items[str(fmt)]=fn
    def get(self,fmt):return self._items[str(fmt)]
    def formats(self):return sorted(self._items)
