from .transform import AlignmentTransform
def translation_fit(source_points,target_points):
    if len(source_points)!=len(target_points) or not source_points:raise ValueError("point sets must have equal nonzero length")
    dx=sum(float(b[0])-float(a[0]) for a,b in zip(source_points,target_points))/len(source_points)
    dy=sum(float(b[1])-float(a[1]) for a,b in zip(source_points,target_points))/len(source_points)
    return AlignmentTransform(dx,dy,1.0,0.0)
