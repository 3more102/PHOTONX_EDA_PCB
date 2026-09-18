class DependencyIndex:
    def __init__(self):self._deps={}
    def add(self,parent,child):self._deps.setdefault(str(parent),set()).add(str(child))
    def descendants(self,key):
        out=set();stack=[str(key)]
        while stack:
            cur=stack.pop()
            for x in self._deps.get(cur,set()):
                if x not in out:out.add(x);stack.append(x)
        return sorted(out)
