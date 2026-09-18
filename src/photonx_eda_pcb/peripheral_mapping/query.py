def bindings_for_component(pmap,component_id):return [x for x in pmap.bindings if x.component_id==str(component_id)]
def controllers(pmap):return sorted({x.component_id for x in pmap.bindings if x.role=="controller"})
