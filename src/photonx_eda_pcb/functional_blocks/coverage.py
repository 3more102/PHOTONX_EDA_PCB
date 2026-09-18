def block_coverage(blocks,component_ids):
    covered={c for b in blocks for c in b.components};allc=set(map(str,component_ids))
    return 1.0 if not allc else round(len(covered&allc)/len(allc),6)
