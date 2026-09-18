class EvidenceService:
    def query(self,db,**kwargs):
        from photonx_eda_pcb.evidence_database.query import query_evidence
        return query_evidence(db,**kwargs)
    def confidence(self,records):
        from photonx_eda_pcb.evidence_database.scoring import object_confidence
        return object_confidence(records)
