class DetectorRegistry:
    def __init__(self):self._detectors=[]
    def register(self,name,fn,priority=0):self._detectors.append((int(priority),str(name),fn));self._detectors.sort(key=lambda x:(-x[0],x[1]))
    def detect(self,path,text):
        results=[]
        for _,name,fn in self._detectors:
            r=fn(path,text)
            if r is not None:results.append((name,r))
        return results
