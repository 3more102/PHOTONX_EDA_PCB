def catalog_manifest(catalog):
    return {'artifacts':[{'name':a.name,'kind':a.kind,'path':a.path,'sha256':a.sha256,'producer':a.producer,'inputs':list(a.inputs),'metadata':a.metadata} for a in (catalog.get(n) for n in catalog.names())]}
