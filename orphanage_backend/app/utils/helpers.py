from bson import ObjectId


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document ObjectId fields to strings.
    Also exposes _id as plain 'id' so the frontend can use o.id directly.
    """
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_doc(i) if isinstance(i, dict) else (str(i) if isinstance(i, ObjectId) else i)
                for i in value
            ]
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        else:
            result[key] = value

    # Always expose _id also as plain "id" for frontend convenience
    if "_id" in result:
        result["id"] = result["_id"]

    return result
