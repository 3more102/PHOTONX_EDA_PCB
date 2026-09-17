class UnionFind:
    def __init__(self,items=()):self.parent={x:x for x in items};self.rank={x:0 for x in items}
    def add(self,x):
        if x not in self.parent:self.parent[x]=x;self.rank[x]=0
    def find(self,x):
        self.add(x)
        if self.parent[x]!=x:self.parent[x]=self.find(self.parent[x])
        return self.parent[x]
    def union(self,a,b):
        ra,rb=self.find(a),self.find(b)
        if ra==rb:return ra
        if self.rank[ra]<self.rank[rb]:ra,rb=rb,ra
        self.parent[rb]=ra
        if self.rank[ra]==self.rank[rb]:self.rank[ra]+=1
        return ra
    def groups(self):
        out={}
        for x in self.parent:out.setdefault(self.find(x),[]).append(x)
        return [sorted(v,key=str) for _,v in sorted(out.items(),key=lambda kv:str(kv[0]))]
