from dataclasses import replace
def transform_placement(placement,scale=1.0,offset_x=0.0,offset_y=0.0,rotation_offset=0.0):
    return replace(placement,x=placement.x*scale+offset_x,y=placement.y*scale+offset_y,rotation=(placement.rotation+rotation_offset)%360.0)
