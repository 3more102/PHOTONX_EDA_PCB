def longest_paths(paths,limit=10):
    return sorted(paths,key=lambda p:(-p.hops,p.nodes))[:int(limit)]
