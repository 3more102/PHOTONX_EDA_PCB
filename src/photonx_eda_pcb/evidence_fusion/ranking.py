def rank_claims(fused):
    return sorted(fused,key=lambda x:(-x.confidence,x.claim))
