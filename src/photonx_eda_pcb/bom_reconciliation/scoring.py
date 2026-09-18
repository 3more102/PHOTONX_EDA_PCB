def reconciliation_score(total_components,discrepancies):
    total=max(0,int(total_components))
    return 1.0 if total==0 else round(max(0.0,1.0-len(discrepancies)/total),6)
