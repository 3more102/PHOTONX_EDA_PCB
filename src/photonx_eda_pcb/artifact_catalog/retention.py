from dataclasses import dataclass
@dataclass(frozen=True)
class RetentionPolicy:
    keep_sources:bool=True;keep_reports:bool=True;keep_intermediate:bool=True
    def keep(self,artifact):
        if artifact.kind=='source':return self.keep_sources
        if artifact.kind=='report':return self.keep_reports
        return self.keep_intermediate
