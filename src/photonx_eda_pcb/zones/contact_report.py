from .connectivity import isolated_islands
def zone_contact_report(zone,contacts):
    members=sorted({x for ids in contacts.values() for x in ids})
    return {"zone_id":zone.id,"layer":zone.layer,"net_id":zone.net_id,"members":members,"island_contacts":{k:list(v) for k,v in sorted(contacts.items())},"isolated_islands":isolated_islands(zone,contacts)}
