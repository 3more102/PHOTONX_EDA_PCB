from dataclasses import dataclass,field
@dataclass(frozen=True)
class KicadExportIssue:
    severity:str
    code:str
    object_id:str
    message:str
@dataclass
class KicadExportReport:
    exported_slots:int=0
    skipped_slots:int=0
    issues:list[KicadExportIssue]=field(default_factory=list)
    @property
    def ok(self):return not any(x.severity=="error" for x in self.issues)
