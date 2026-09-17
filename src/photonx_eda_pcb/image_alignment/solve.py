def solve_linear(matrix,vector):
    a=[list(map(float,row))+[float(value)] for row,value in zip(matrix,vector)]; n=len(a)
    for col in range(n):
        pivot=max(range(col,n),key=lambda row:abs(a[row][col]))
        if abs(a[pivot][col])<1e-12: raise ValueError("singular alignment system")
        a[col],a[pivot]=a[pivot],a[col]
        scale=a[col][col]; a[col]=[value/scale for value in a[col]]
        for row in range(n):
            if row==col: continue
            factor=a[row][col]; a[row]=[left-factor*right for left,right in zip(a[row],a[col])]
    return [a[row][-1] for row in range(n)]
