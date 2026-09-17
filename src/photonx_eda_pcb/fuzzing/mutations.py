def mutate_text(text,index=0,replacement='?'):
    if not text:return replacement
    i=max(0,min(int(index),len(text)-1))
    return text[:i]+replacement+text[i+1:]

def truncate(text,length):return text[:max(0,int(length))]

def duplicate_slice(text,start,end):return text[:end]+text[start:end]+text[end:]
