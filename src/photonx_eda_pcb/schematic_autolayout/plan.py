from .model import AutoLayoutPlan
def build_layout_plan(partition,x_step=30.0,y_step=20.0,grid=2.54):
    return AutoLayoutPlan(partition.id,tuple(partition.component_ids),tuple(partition.net_ids),float(x_step),float(y_step),float(grid))
