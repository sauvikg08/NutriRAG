from qdrant_client import QdrantClient, models
client = QdrantClient("http://localhost:6333")

model_handle =  "BAAI/bge-small-en-v1.5"
collection_name = 'NutriRAG'

def create_collection():
    client.recreate_collection(                     #If collection already exists
        collection_name = collection_name,
        vectors_config = models.VectorParams(
            size = 384,
            distance=models.Distance.COSINE
        )
    )