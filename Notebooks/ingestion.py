import pandas as pd
from qdrant_client import QdrantClient, models
client = QdrantClient("http://localhost:6333")

model_handle =  "BAAI/bge-small-en-v1.5"
collection_name = 'NutriRAG'

client.recreate_collection(                     #If collection already exists
    collection_name = collection_name,
    vectors_config = models.VectorParams(
        size = 384,
        distance=models.Distance.COSINE
    )
)

points = []
id = 0
def load_data(load_path = '../data/data.csv'):
    data = pd.read_csv(load_path)
    documents = data.to_dict(orient = 'records')

    points = []
    id = 0

    for doc in documents:
        point = models.PointStruct(
            id=id,
            vector=models.Document(text = doc['food_name'], model = model_handle),
            payload = {
                "food_name": doc["food_name"],
                "meal_type": doc["meal_type"],
                "food_type": doc["food_type"],
                "serving_size": doc["serving_size"],

                # Macros
                "calories_kcal": doc["calories_kcal"],
                "protein_g": doc["protein_g"],
                "carbs_g": doc["carbs_g"],
                "fats_g": doc["fats_g"],
                "fiber_g": doc["fiber_g"],

                # Fat breakdown
                "saturated_fat_g": doc["saturated_fat_g"],
                "monounsaturated_fat_g": doc["monounsaturated_fat_g"],
                "polyunsaturated_fat_g": doc["polyunsaturated_fat_g"],
                "trans_fat_g": doc["trans_fat_g"],

                # Micros
                "sodium_mg": doc["sodium_mg"],
                "calcium_mg": doc["calcium_mg"],
                "phosphorus_mg": doc["phosphorus_mg"]
            }
        )

        points.append(point)
        id+=1

    client.upsert(
        collection_name=collection_name,
        points=points
        )
    return client

if __name__=="__main__":
    load_data()
