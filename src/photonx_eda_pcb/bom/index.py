def by_reference(items):
    result={}
    for item in items:
        for reference in item.references: result[reference]=item
    return dict(sorted(result.items()))
