from __future__ import annotations
import tkinter as tk
from .state import ViewState
from ..via_review import build_via_review_descriptors


class BoardCanvas(tk.Canvas):
    def __init__(self, master, state: ViewState, on_select=None, **kwargs):
        super().__init__(master, background="white", **kwargs); self.state = state; self.on_select = on_select
        self.bind("<Button-1>", self._click); self.bind("<MouseWheel>", self._wheel); self.bind("<Configure>", lambda _e: self.redraw()); self.redraw()

    def xy(self, x, y):
        s = self.state.scale; return self.state.offset_x + x * s, self.state.offset_y + y * s

    def redraw(self):
        self.delete("all"); b = self.state.board; highlighted = self.state.highlighted_net_id
        for seg in b.outline:
            x1,y1=self.xy(seg.start.x,seg.start.y); x2,y2=self.xy(seg.end.x,seg.end.y); self.create_line(x1,y1,x2,y2,width=2,tags=(seg.id,"outline"))
        for trk in b.tracks:
            x1,y1=self.xy(trk.start.x,trk.start.y); x2,y2=self.xy(trk.end.x,trk.end.y); width=max(2,trk.width*self.state.scale); dash=() if highlighted in {None,trk.net_id} else (2,3); self.create_line(x1,y1,x2,y2,width=width,capstyle=tk.ROUND,dash=dash,tags=(trk.id,"track"))
        for pad in b.pads:
            x,y=self.xy(pad.center.x,pad.center.y); rx=pad.size_x*self.state.scale/2; ry=pad.size_y*self.state.scale/2; stipple="" if highlighted in {None,pad.net_id} else "gray50"; self.create_oval(x-rx,y-ry,x+rx,y+ry,width=2,stipple=stipple,tags=(pad.id,"pad"))
        for via in build_via_review_descriptors(b):
            x,y=self.xy(via.x,via.y); radius=max(3.0,via.diameter*self.state.scale/2)
            dash={"exportable":(),"omitted":(6,3),"unproven":(2,3),"invalid":(1,2)}.get(via.status,(1,2))
            stipple="" if highlighted in {None,via.net_id} else "gray50"
            self.create_oval(
                x-radius,y-radius,x+radius,y+radius,
                width=3 if via.proven else 2,
                dash=dash,
                stipple=stipple,
                tags=(via.drill_id,"via",f"via-status:{via.status}"),
            )
        if self.state.selected_id:
            for item in self.find_withtag(self.state.selected_id): self.itemconfigure(item,width=4)

    def _click(self,event):
        items=self.find_overlapping(event.x-3,event.y-3,event.x+3,event.y+3); selected=None
        if items:
            tags=self.gettags(items[-1]); selected=tags[0] if tags else None
        self.state.selected_id=selected
        if self.on_select: self.on_select(selected)
        self.redraw()

    def _wheel(self,event):
        factor=1.15 if event.delta>0 else 1/1.15; self.state.scale=min(100.0,max(2.0,self.state.scale*factor)); self.redraw()
