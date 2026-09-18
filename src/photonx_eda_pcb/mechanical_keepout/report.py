def keepout_report(violations):return [{"keepout_id":v.keepout_id,"object_id":v.object_id,"kind":v.kind} for v in violations]
