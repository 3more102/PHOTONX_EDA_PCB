def variant_reconciliation_summary(bom_issues,placement_deltas):
    return {"bom_issues":len(bom_issues),"placement_mismatches":sum(x.code!="OK" for x in placement_deltas),"ready":not bom_issues and all(x.code=="OK" for x in placement_deltas)}
