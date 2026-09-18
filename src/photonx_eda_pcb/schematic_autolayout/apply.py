from .model import AutoLayoutResult
from .place import place_components
from .route import route_page_nets
def apply_layout(graph,plan):
    layout=place_components(graph,plan);routes,crossings=route_page_nets(graph,layout.positions,plan.net_ids)
    return AutoLayoutResult(plan.page_id,{k:(v.x,v.y) for k,v in sorted(layout.positions.items())},routes,crossings)
