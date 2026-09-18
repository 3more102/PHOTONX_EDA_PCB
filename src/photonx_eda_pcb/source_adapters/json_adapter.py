import json
from .base import SourceAdapter
from .model import SourceDocument
class JsonAdapter(SourceAdapter):
    format_name="json"
    def read(self,path,text):return SourceDocument(str(path),"json",json.loads(text),{"length":len(str(text))})
