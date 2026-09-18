def grid_points(size):
    n=max(0,int(size));return [(float(i),float(j)) for i in range(n) for j in range(n)]
def chain_edges(size):
    n=max(0,int(size));return [(str(i),str(i+1)) for i in range(max(0,n-1))]
