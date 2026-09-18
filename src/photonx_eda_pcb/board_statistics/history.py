class StatsHistory:
    def __init__(self):self._items=[]
    def add(self,label,stats):self._items.append((str(label),stats));return stats
    def all(self):return list(self._items)
    def latest(self):return self._items[-1] if self._items else None
