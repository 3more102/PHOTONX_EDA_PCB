def editing_summary(state):return {"pending":len(state.pending),"applied":len(state.applied),"pending_ids":[x.id for x in state.pending]}
