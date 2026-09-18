class AdapterRegistry:
    def __init__(self):self._items={}
    def register(self,fmt,adapter):
        if fmt in self._items:raise ValueError(f"duplicate adapter {fmt}")
        self._items[str(fmt)]=adapter
    def get(self,fmt):return self._items[str(fmt)]
    def formats(self):return sorted(self._items)
    def resolve(self,guess):return self._items.get(guess.format)
