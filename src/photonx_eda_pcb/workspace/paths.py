from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True)
class WorkspacePaths:
    root:Path
    @property
    def evidence(self): return self.root/"evidence"
    @property
    def exports(self): return self.root/"exports"
    @property
    def reports(self): return self.root/"reports"
    def ensure(self):
        for path in (self.root,self.evidence,self.exports,self.reports): path.mkdir(parents=True,exist_ok=True)
