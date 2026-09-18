class SnapshotTags:
    def __init__(self):self._tags={}
    def set(self,name,snapshot_id):self._tags[str(name)]=str(snapshot_id)
    def get(self,name):return self._tags[str(name)]
    def all(self):return dict(sorted(self._tags.items()))
