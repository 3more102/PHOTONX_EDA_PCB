from collections import defaultdict
class LayerConnectivityGraph:
    def __init__(self): self.adj=defaultdict(set)
    def add_node(self,node): self.adj[node]
    def add_edge(self,a,b): self.adj[a].add(b); self.adj[b].add(a)
    def neighbors(self,node): return tuple(sorted(self.adj.get(node,())))
    def nodes(self): return tuple(sorted(self.adj))
