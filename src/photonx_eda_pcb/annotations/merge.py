from .model import AnnotationStore
def merge_annotation_stores(*stores):
    by={}
    for s in stores:
        for x in s.items:by[x.id]=x
    return AnnotationStore([by[k] for k in sorted(by)])
