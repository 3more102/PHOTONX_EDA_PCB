def normalize_member_map(net_members): return {str(k):set(map(str,v)) for k,v in net_members.items()}
