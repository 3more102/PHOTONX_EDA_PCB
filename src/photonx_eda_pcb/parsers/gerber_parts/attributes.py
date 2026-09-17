from ..common.attributes import parse_attribute_fields
def parse_x2_attribute(text:str)->dict[str,object]:
    name,values=parse_attribute_fields(text)
    return {"name":name,"values":values}
