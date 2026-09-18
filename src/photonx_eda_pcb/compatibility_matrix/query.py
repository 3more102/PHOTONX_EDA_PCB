def compatibility_for(matrix,*,feature=None,format=None,status=None):
    return [e for e in matrix.entries if (feature is None or e.feature==feature) and (format is None or e.format==format) and (status is None or e.status==status)]
