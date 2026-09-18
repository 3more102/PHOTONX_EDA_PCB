def matrix_report(m):
    return [{"feature":e.feature,"format":e.format,"status":e.status,"notes":e.notes,"tests":list(e.tests)} for e in sorted(m.entries,key=lambda x:(x.feature,x.format))]
