class ValidationRegistry:
    def __init__(self):self._items={}
    def register(self,check,fn):
        if check.name in self._items:raise ValueError("duplicate validation check")
        self._items[check.name]=(check,fn)
    def items(self):return [self._items[k] for k in sorted(self._items)]
