from .affine import Affine2D
from .solve import solve_linear
def fit_affine(points):
    pts=list(points)
    if len(pts)!=3: raise ValueError("exactly three control points are required for affine fit")
    matrix=[]; vector=[]
    for p in pts:
        matrix.append([p.image_x,p.image_y,1,0,0,0]); vector.append(p.board_x)
        matrix.append([0,0,0,p.image_x,p.image_y,1]); vector.append(p.board_y)
    return Affine2D(*solve_linear(matrix,vector))
