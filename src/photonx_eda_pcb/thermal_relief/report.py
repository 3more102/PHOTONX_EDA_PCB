from .symmetry import is_symmetric

def thermal_report(items):
    return {'count':len(items),'symmetric':sum(is_symmetric(x.spokes) for x in items),'inferred':sum(x.inferred for x in items)}
