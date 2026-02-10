from collection import client, collection_name, model_handle
from qdrant_client import models

def extract_query(query):
    query = query.lower()

    meal_type = None
    food_type = None
    rank_by = None

    # ---- Food type filters ----
    veg_terms = {"veg", "vegetarian", "plant based"}
    non_veg_terms = {"non veg", "chicken", "fish", "egg", "non-veg"}

    if any(term in query for term in non_veg_terms):
        food_type = "non-veg"
    elif any(term in query for term in veg_terms):
        food_type = "veg"

    # ---- Meal type filters ----
    if "breakfast" in query:
        meal_type = "breakfast"
    elif "lunch" in query:
        meal_type = "lunch"
    elif "dinner" in query:
        meal_type = "dinner"
    elif "snack" in query:
        meal_type = "snacks"

    # ---- Ranking intent (NOT filters) ----
    if "high protein" in query:
        rank_by = ("protein_g", True)
    elif "high carb" in query:
        rank_by = ("carbs_g", True)
    elif "low calorie" in query:
        rank_by = ("calories_kcal", False)

    return food_type, meal_type, rank_by

def search_with_filter(query, meal_type='', food_type = '', limit = 20):

    must_conditions = []

    if meal_type:
        must_conditions.append(
            models.FieldCondition(
                    key= 'meal_type',
                    match=models.MatchValue(value=meal_type)

            )
        )
    if food_type:
        must_conditions.append(
            models.FieldCondition(
                    key= 'food_type',
                    match=models.MatchValue(value=food_type)
                )
        )



    results = client.query_points(
        collection_name = collection_name,
        query = models.Document(
            text=query,
            model = model_handle
        ),

        query_filter=models.Filter( 
            must=must_conditions if must_conditions else None
        ),
        limit=limit,
        with_payload=True 
    )

    return results
