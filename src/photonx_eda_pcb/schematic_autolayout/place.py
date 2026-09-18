from photonx_eda_pcb.graph_layout import layout_components
from photonx_eda_pcb.graph_layout.normalize import normalize_layout
def place_components(graph,plan):
    layout=layout_components(graph,plan.component_ids,plan.x_step,plan.y_step)
    return normalize_layout(layout,(20,20),plan.grid)
