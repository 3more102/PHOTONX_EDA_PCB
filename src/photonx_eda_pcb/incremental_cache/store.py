class IncrementalCache:
    def __init__(self):self._data={};self.hits=0;self.misses=0
    def get(self,key,default=None):
        if key in self._data:self.hits+=1;return self._data[key]
        self.misses+=1;return default
    def put(self,key,value):self._data[str(key)]=value;return value
    def invalidate(self,key):return self._data.pop(str(key),None)
    def clear(self):self._data.clear()
    def __len__(self):return len(self._data)
