class MiddlewareChain:
    def __init__(self,*items):self.items=list(items)
    def apply(self,command,context=None):
        cur=command
        for fn in self.items:cur=fn(cur,context)
        return cur
