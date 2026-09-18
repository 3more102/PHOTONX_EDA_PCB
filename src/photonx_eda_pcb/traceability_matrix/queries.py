def links_for_object(matrix,object_id):return [x for x in matrix.links if str(object_id) in x.object_ids]
def links_for_artifact(matrix,artifact_id):return [x for x in matrix.links if str(artifact_id) in x.artifact_ids]
def unresolved_traceability(matrix):return [x for x in matrix.links if not x.source_ids or not x.artifact_ids]
