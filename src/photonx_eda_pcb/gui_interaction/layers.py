from dataclasses import dataclass,field
@dataclass
class LayerVisibility:
    visible:dict[str,bool]=field(default_factory=dict)
    def set(self,layer,value):self.visible[str(layer)]=bool(value);return self
    def is_visible(self,layer):return self.visible.get(str(layer),True)
