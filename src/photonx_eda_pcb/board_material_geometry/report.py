from .metrics import material_metrics
from .cutouts import cutout_polygons
def material_report(board):
    from .material import board_material_shape
    shape=board_material_shape(board)
    out=material_metrics(shape);out["cutouts"]=len(cutout_polygons(board))
    return out
