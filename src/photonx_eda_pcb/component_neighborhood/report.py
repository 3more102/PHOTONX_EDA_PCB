def neighborhood_report(items):return [{"component_id":x.component_id,"degree":x.degree,"nets":list(x.nets),"neighbors":list(x.neighbors),"kinds":list(x.kinds)} for x in items]
