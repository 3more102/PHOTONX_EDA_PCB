def partition_report(parts):return [{"id":p.id,"title":p.title,"blocks":list(p.block_ids),"components":list(p.component_ids),"nets":list(p.net_ids),"weight":p.weight} for p in parts]
