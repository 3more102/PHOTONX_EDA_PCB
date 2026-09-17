from dataclasses import dataclass
@dataclass
class WorkspaceLock:
    owner:str|None=None
    def acquire(self,owner):
        if self.owner is not None and self.owner!=owner:return False
        self.owner=owner; return True
    def release(self,owner):
        if self.owner!=owner:return False
        self.owner=None; return True
