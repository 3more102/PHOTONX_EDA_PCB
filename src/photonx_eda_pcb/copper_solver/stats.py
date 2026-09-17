def solver_stats(result):
    sizes=[len(g) for g in result.groups]
    return {'groups':len(sizes),'objects':sum(sizes),'edges':len(result.edges),'largest_group':max(sizes,default=0),'diagnostics':len(result.diagnostics)}
