def world_to_screen(x,y,viewport,width,height):
    return ((x-viewport.center_x)*viewport.zoom+width/2,(viewport.center_y-y)*viewport.zoom+height/2)
def screen_to_world(x,y,viewport,width,height):
    return ((x-width/2)/viewport.zoom+viewport.center_x,viewport.center_y-(y-height/2)/viewport.zoom)
