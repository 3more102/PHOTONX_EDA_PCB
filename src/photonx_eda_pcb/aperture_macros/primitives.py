SUPPORTED={1:"circle",2:"vector_line",4:"outline",5:"polygon",6:"moire",7:"thermal",20:"vector_line",21:"center_line",22:"lower_left_line"}
def primitive_name(code): return SUPPORTED.get(int(code),"unsupported")
