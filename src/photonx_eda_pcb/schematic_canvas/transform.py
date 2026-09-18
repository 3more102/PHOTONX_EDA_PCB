def world_to_screen(point,viewport,width,height):
    x=(float(point[0])-viewport.center_x)*viewport.zoom+float(width)/2
    y=(float(point[1])-viewport.center_y)*viewport.zoom+float(height)/2
    return (x,y)
def screen_to_world(point,viewport,width,height):
    if viewport.zoom==0:raise ValueError("zero zoom")
    x=(float(point[0])-float(width)/2)/viewport.zoom+viewport.center_x
    y=(float(point[1])-float(height)/2)/viewport.zoom+viewport.center_y
    return (x,y)
