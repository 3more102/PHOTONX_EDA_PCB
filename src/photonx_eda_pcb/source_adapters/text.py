from .base import SourceAdapter
from .model import SourceDocument
class TextAdapter(SourceAdapter):
    def __init__(self,format_name):self.format_name=str(format_name)
    def read(self,path,text):return SourceDocument(str(path),self.format_name,str(text),{"length":len(str(text))})
