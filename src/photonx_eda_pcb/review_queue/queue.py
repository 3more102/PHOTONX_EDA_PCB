class ReviewQueue:
    def __init__(self): self._items={}
    def add(self,item):
        if item.id in self._items: raise ValueError(f"review item already exists: {item.id}")
        self._items[item.id]=item
    def get(self,item_id): return self._items.get(item_id)
    def open_items(self): return tuple(sorted((item for item in self._items.values() if item.status=="open"),key=lambda item:(item.confidence,item.id)))
    def all(self): return tuple(self._items[key] for key in sorted(self._items))
