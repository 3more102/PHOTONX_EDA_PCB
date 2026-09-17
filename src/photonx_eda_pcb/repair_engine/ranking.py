RISK={'remove_zero_area':0,'clear_stale_net_link':0,'bridge_gap':2,'review_self_touch':3}
def rank_candidates(candidates):return sorted(candidates,key=lambda c:(RISK.get(c.kind,9),-c.confidence,c.kind,c.object_ids))
def top_candidates(candidates,limit=20):return rank_candidates(candidates)[:max(0,limit)]
