def hierarchy_coverage(result,total_components):
    assigned=len({c for b in result.blocks for c in b.component_ids})
    return 1.0 if total_components==0 else round(assigned/total_components,6)
