def snapshot_lineage_ids(snapshot_store):return [x.id for x in snapshot_store.lineage()]
def approved_change_ids(eco_set):return sorted(x.id for x in eco_set.changes if x.approved)
