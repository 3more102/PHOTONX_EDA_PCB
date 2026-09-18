class ViewportController:
    def __init__(self,viewport):self.viewport=viewport
    def pan(self,dx,dy):return self.viewport.pan(dx,dy)
    def zoom(self,factor):return self.viewport.zoom_by(factor)
    def fit_bounds(self,bounds,width,height,padding=.05):
        x0,y0,x1,y1=map(float,bounds);bw=max(x1-x0,1e-9);bh=max(y1-y0,1e-9)
        self.viewport.center_x=(x0+x1)/2;self.viewport.center_y=(y0+y1)/2
        self.viewport.zoom=min(width/(bw*(1+padding*2)),height/(bh*(1+padding*2)))
        return self.viewport
