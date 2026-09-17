class MemoryCache:
    def __init__(self,max_items=1024): self.max_items=max_items; self._items={}; self._order=[]
    def get(self,key,default=None): return self._items.get(key,default)
    def put(self,key,value):
        if key not in self._items:self._order.append(key)
        self._items[key]=value
        while len(self._order)>self.max_items:
            old=self._order.pop(0); self._items.pop(old,None)
    def clear(self): self._items.clear(); self._order.clear()
    def __len__(self): return len(self._items)
