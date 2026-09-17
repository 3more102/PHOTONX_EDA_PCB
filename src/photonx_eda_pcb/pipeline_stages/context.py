from dataclasses import dataclass,field
@dataclass
class PipelineContext:
    inputs:dict=field(default_factory=dict);artifacts:dict=field(default_factory=dict);diagnostics:list=field(default_factory=list);metadata:dict=field(default_factory=dict)
    def put(self,name,value):self.artifacts[name]=value;return value
    def get(self,name,default=None):return self.artifacts.get(name,default)
