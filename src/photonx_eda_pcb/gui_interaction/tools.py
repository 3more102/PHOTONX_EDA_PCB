from dataclasses import dataclass
@dataclass
class ToolState:
    active:str="select"
    previous:str|None=None
    def activate(self,name):self.previous=self.active;self.active=str(name);return self
