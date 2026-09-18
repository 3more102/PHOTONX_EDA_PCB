def eco_release_ready(eco):return bool(eco.changes) and all(x.approved for x in eco.changes)
