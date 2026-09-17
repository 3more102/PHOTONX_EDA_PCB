from dataclasses import dataclass,field
@dataclass
class BenchmarkBaseline:
    values:dict[str,float]=field(default_factory=dict);metadata:dict=field(default_factory=dict)
    def get(self,name):return self.values.get(name)
    def set(self,name,value):self.values[name]=float(value)
