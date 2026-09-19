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
    exported_regions:int=0
    skipped_regions:int=0
    exported_npth_slots:int=0
    exported_plated_slots:int=0
    exported_tracks:int=0
    skipped_tracks:int=0
    skipped_routes:int=0
    issues:list[KicadExportIssue]=field(default_factory=list)
    exported_slot_ids:list[str]=field(default_factory=list)
    skipped_slot_ids:list[str]=field(default_factory=list)
    exported_region_ids:list[str]=field(default_factory=list)
    skipped_region_ids:list[str]=field(default_factory=list)
    exported_track_ids:list[str]=field(default_factory=list)
    skipped_track_ids:list[str]=field(default_factory=list)
    skipped_route_ids:list[str]=field(default_factory=list)
    @property
    def ok(self):return not any(x.severity=="error" for x in self.issues)
