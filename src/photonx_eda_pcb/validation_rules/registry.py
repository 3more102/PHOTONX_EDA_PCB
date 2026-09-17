from dataclasses import dataclass,field
from typing import Callable
Rule=Callable[[object],list]
@dataclass
class RuleRegistry:
    rules:dict[str,Rule]=field(default_factory=dict)
    def register(self,name:str,rule:Rule):
        if name in self.rules: raise ValueError(f'duplicate rule {name}')
        self.rules[name]=rule
        return rule
    def run(self,board):
        out=[]
        for name in sorted(self.rules): out.extend(self.rules[name](board))
        return out
