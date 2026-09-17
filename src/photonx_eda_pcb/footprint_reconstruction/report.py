def footprint_report(items):
    return {'count':len(items),'with_reference':sum(bool(x.reference) for x in items),'with_package_hint':sum(bool(x.package_hint) for x in items),'avg_confidence':round(sum(x.confidence for x in items)/len(items),6) if items else 0.0}
