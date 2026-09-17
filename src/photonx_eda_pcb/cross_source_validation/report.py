from .conflicts import find_conflicts

def cross_source_report(items):
    conflicts=find_conflicts(items)
    return {'observations':len(items),'conflicts':len(conflicts),'details':conflicts}
