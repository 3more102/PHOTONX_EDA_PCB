def weakest_pairs(items):return sorted(items,key=lambda x:(x.score,x.positive_net,x.negative_net))
