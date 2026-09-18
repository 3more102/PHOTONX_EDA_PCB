def discrepancies_report(items):
    return [{"reference":x.reference,"code":x.code,"expected":x.expected,"observed":x.observed} for x in items]
