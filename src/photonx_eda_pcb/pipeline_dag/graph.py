class PipelineDag:
    def __init__(self):self.nodes={}
    def add(self,node):
        if node.name in self.nodes:raise ValueError(f"duplicate dag node: {node.name}")
        self.nodes[node.name]=node;return self
    def names(self):return sorted(self.nodes)
    def producer_map(self):
        out={}
        for n in self.nodes.values():
            for key in n.produces:
                if key in out:raise ValueError(f"multiple producers for artifact: {key}")
                out[key]=n.name
        return out
