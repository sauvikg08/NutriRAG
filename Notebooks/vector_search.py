from qdrant import models
from collection import client, collection_name, model_handle

def vector_search(query, limit = 5):
    results = client.query_points(
        collection_name = collection_name,
        query = models.Document(
            text=query,
            model = model_handle
        ),
    limit = limit,
    with_payload = True
    )
    return results