import zlib
def crc32_text(text:str)->str: return f"{zlib.crc32(text.encode('utf-8')) & 0xffffffff:08x}"
