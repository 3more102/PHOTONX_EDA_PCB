class MigrationRegistry:
    def __init__(self):self._m={}
    def add(self,migration):
        key=(migration.from_version,migration.to_version)
        if key in self._m:raise ValueError(f"duplicate migration {key}")
        if migration.to_version<=migration.from_version:raise ValueError("migration must increase version")
        self._m[key]=migration
    def next_from(self,version):
        candidates=[m for (a,_),m in self._m.items() if a==int(version)]
        if not candidates:return None
        return min(candidates,key=lambda m:m.to_version)
