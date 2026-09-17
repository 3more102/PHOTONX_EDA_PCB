from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from .models import BoardModel

class BoardViewer(tk.Tk):
    def __init__(self, board: BoardModel):
        super().__init__(); self.title('PHOTONX EDA PCB'); self.geometry('1000x650'); self.board=board
        self.scale=12.0; self.ox=80; self.oy=80; self.selected_net=None
        left=ttk.Frame(self); left.pack(side='left',fill='y')
        ttk.Label(left,text='Nets').pack(anchor='w')
        self.list=tk.Listbox(left,width=24); self.list.pack(fill='y',expand=True)
        for n in board.nets: self.list.insert('end',n)
        self.list.bind('<<ListboxSelect>>',self._net)
        self.info=tk.Text(left,width=28,height=12); self.info.pack(fill='x')
        self.canvas=tk.Canvas(self,bg='#111827'); self.canvas.pack(side='right',fill='both',expand=True)
        self.canvas.bind('<MouseWheel>',self._zoom); self.canvas.bind('<Button-1>',self._click)
        self.draw()
    def xy(self,p): return self.ox+p.x*self.scale,self.oy+p.y*self.scale
    def draw(self):
        c=self.canvas; c.delete('all')
        for s in self.board.outline.segments:
            a=self.xy(s.start); b=self.xy(s.end); c.create_line(*a,*b,fill='white',width=2)
        for t in self.board.tracks:
            a=self.xy(t.start); b=self.xy(t.end); active=(self.selected_net==t.net)
            c.create_line(*a,*b,fill='#f59e0b' if active else '#22c55e',width=max(2,t.width*self.scale),tags=('obj',t.id))
        for p in self.board.pads:
            x,y=self.xy(p.center); r=p.diameter*self.scale/2; active=(self.selected_net==p.net)
            c.create_oval(x-r,y-r,x+r,y+r,fill='#fde047' if active else '#f97316',outline='black',tags=('obj',p.id))
            c.create_text(x,y-r-10,text=p.id,fill='white')
    def _net(self,_):
        sel=self.list.curselection(); self.selected_net=self.list.get(sel[0]) if sel else None; self.draw()
    def _zoom(self,e):
        self.scale*=1.15 if e.delta>0 else 1/1.15; self.draw()
    def _click(self,e):
        ids=self.canvas.find_overlapping(e.x-3,e.y-3,e.x+3,e.y+3)
        self.info.delete('1.0','end')
        for item in reversed(ids):
            tags=self.canvas.gettags(item)
            if 'obj' in tags:
                oid=tags[-1]; obj=next((o for o in [*self.board.pads,*self.board.tracks] if o.id==oid),None)
                if obj: self.info.insert('end',repr(obj)); break

def show(board: BoardModel): BoardViewer(board).mainloop()
