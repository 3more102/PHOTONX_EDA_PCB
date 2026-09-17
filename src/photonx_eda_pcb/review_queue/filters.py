def by_kind(items,kind): return tuple(item for item in items if item.kind==kind)
def below_confidence(items,threshold): return tuple(item for item in items if item.confidence<threshold)
