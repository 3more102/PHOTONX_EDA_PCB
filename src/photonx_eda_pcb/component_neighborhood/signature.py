def neighborhood_signature(n):
    return (n.degree,tuple(sorted(n.kinds)),len(n.nets))
