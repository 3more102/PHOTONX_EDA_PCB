from dataclasses import dataclass
@dataclass
class Viewport:
    center_x:float=0.0
    center_y:float=0.0
    zoom:float=1.0
    def pan(self,dx,dy):self.center_x+=float(dx);self.center_y+=float(dy);return self
    def zoom_by(self,factor,min_zoom=.01,max_zoom=1000):
        self.zoom=max(min_zoom,min(max_zoom,self.zoom*float(factor)));return self
