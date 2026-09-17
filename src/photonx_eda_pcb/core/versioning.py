MODEL_SCHEMA_VERSION="1.0"
REPORT_SCHEMA_VERSION="1.0"
def compatible_schema(version:str)->bool: return version.split(".",1)[0]==MODEL_SCHEMA_VERSION.split(".",1)[0]
