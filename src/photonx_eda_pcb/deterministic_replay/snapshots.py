def snapshot_replay_match(snapshot_store,replay_result):
    head=snapshot_store.head()
    return {"snapshot_available":head is not None,"replay_deterministic":replay_result.passed,"snapshot_sha256":None if head is None else head.sha256}
