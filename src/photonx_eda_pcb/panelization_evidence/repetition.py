def same_size(a,b,tol=0.05):
    aw,ah=a[2]-a[0],a[3]-a[1];bw,bh=b[2]-b[0],b[3]-b[1]
    return abs(aw-bw)<=tol and abs(ah-bh)<=tol
def repeated_groups(bounds_list,tol=0.05):
    groups=[]
    for b in bounds_list:
        for g in groups:
            if same_size(g[0],b,tol):g.append(b);break
        else:groups.append([b])
    return [g for g in groups if len(g)>1]
