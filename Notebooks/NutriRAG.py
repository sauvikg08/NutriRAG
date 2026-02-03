#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from qdrant_client import QdrantClient, models


# ## Reading the DataFrame

# In[2]:


df = pd.read_csv('data/data.csv')


# In[3]:


df.head()


# In[4]:


documents = df.to_dict(orient='records')


# In[5]:


documents[0]


# # Retrieval

# ## Loading Qdrant

# In[6]:


client = QdrantClient("http://localhost:6333")


# In[7]:


from fastembed import TextEmbedding
TextEmbedding.list_supported_models()


# ### Choosing correct Model

# In[8]:


import json

EMBEDDING_DIMENSIONALITY = 384

for model in TextEmbedding.list_supported_models():
    if model["dim"] == EMBEDDING_DIMENSIONALITY:
        print(json.dumps(model, indent=2))


# In[9]:


model_handle =  "BAAI/bge-small-en-v1.5"
collection_name = 'NutriRAG'


# In[10]:


client.recreate_collection(                     #If collection already exists
    collection_name = collection_name,
    vectors_config = models.VectorParams(
        size = 384,
        distance=models.Distance.COSINE
    )
)


# In[11]:


points = []
id = 0


# In[12]:


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


# In[13]:


client.upsert(
    collection_name=collection_name,
    points=points
    )


# In[14]:


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



# In[15]:


test = vector_search('High protein non-vegetarian dinner')
test


# In[16]:


test.points


# In[17]:


print(test)


# In[18]:


for t in test.points:
    print(t.payload['food_name'], t.payload['meal_type'], t.payload['food_type'], t.payload['protein_g'])


# Why nutrition values are NOT stored in embeddings
# 
# Embedding models (BGE-small, MiniLM, OpenAI, etc.) capture semantic meaning, not numeric magnitude.
# Numeric nutrition values like:
# 
# protein_g
# 
# calories_kcal
# 
# sodium_mg
# 
# cannot be understood correctly by embeddings.
# For example:
# 
# “Protein Bar” may embed strongly for “protein”
# even if the actual protein value is low.
# 
# To solve this, the search engine uses a two-stage ranking pipeline:
# 
# Semantic Recall (embedding-based)
# Retrieve foods that are semantically related to the query.
# 
# Nutrition-Aware Re-Ranking (metadata-based)
# Sort or score results using actual nutrition values
# (e.g., highest protein, lowest calories, lowest sodium).
# 
# This produces search results that are both semantically relevant and nutritionally correct, which is essential for diet planning.

# In[19]:


client.create_payload_index(
    collection_name = collection_name,
    field_name = 'meal_type',
    field_schema = 'keyword'
)


# In[20]:


client.create_payload_index(
    collection_name = collection_name,
    field_name = 'food_type',
    field_schema = 'keyword'
)


# In[21]:


query = 'Suggest me high protein non veg dinner'


# In[22]:


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


# In[23]:


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


# In[50]:


def search(query, limit=10):
    food, meal, rank = extract_query(query)
    result = search_with_filter(query = query,meal_type = meal,food_type = food, limit = limit * 5)
    points = result.points
    if rank:
        field, descend = rank
        points = sorted(points, key = lambda p:p.payload[field],
        reverse = descend
                       )
    return points[:limit]


# In[25]:


test = search(query, 10)
test


# In[26]:


for t in test:
    print(t.payload['food_name'], t.payload['meal_type'], t.payload['food_type'], t.payload['protein_g'])


# # Generation

# In[27]:


import google.generativeai as genai
genai.configure()
model = genai.GenerativeModel("gemini-2.5-flash")


# In[28]:


response = model.generate_content(query)


# In[29]:


print(response.text)


# In[30]:


## Building a prompt

prompt_template = """
You are a professional dietician and nutrition expert.

Answer the QUESTION using ONLY the food items and nutrition information listed below.
Do NOT invent foods, nutrition values, or meals that are not provided.

Your responsibilities:
- Select suitable food items based on the user's request
- Combine them into a sensible meal or meal plan
- Match the requested meal type, food preference, and nutrition goal
- Use a clear, professional, and natural tone.
- Do not mention any reference data in output

IMPORTANT OUTPUT RULES:
1. Always list each selected food item separately.
2. For EACH food item, include:
   - Food name
   - Serving size
   - Calories
   - Protein
   - Carbohydrates
   - Fats
3. After listing individual items, provide a TOTAL nutrition summary.
4. Explain choices briefly, without comparing to foods not selected.
5. Do NOT mention sources, databases, or internal mechanisms.

If the QUESTION asks for a meal or diet plan:
- Organize the response by meal (e.g., Dinner, Breakfast)
- Choose foods only from the list below
- Give options for breakfast, lunch, dinner and snack. 
- If suitable items are not available for a specific meal, state this explicitly instead of omitting the meal.

QUESTION:
{question}

AVAILABLE FOODS:
{context}
""".strip()


entry_template = """
food_name: {food_name}
meal_type: {meal_type}
food_type: {food_type}
serving_size: {serving_size}
calories_kcal: {calories_kcal}
protein_g: {protein_g}
carbs_g: {carbs_g}
fats_g: {fats_g}
fiber_g: {fiber_g}
saturated_fat_g: {saturated_fat_g}
monounsaturated_fat_g: {monounsaturated_fat_g}
polyunsaturated_fat_g: {polyunsaturated_fat_g}
trans_fat_g: {trans_fat_g}
sodium_mg: {sodium_mg}
calcium_mg: {calcium_mg}
phosphorus_mg: {phosphorus_mg}
""".strip()



def build_prompt(query, search_results):
    context = ""

    for point in search_results:
        context += entry_template.format(**point.payload) + "\n\n"

    prompt = prompt_template.format(
        question=query,
        context=context
    ).strip()

    return prompt



# In[31]:


def llm(prompt):

    response = model.generate_content(prompt)
    return response.text


# In[32]:


def rag(query, limit=5):
    docs = search(query, limit)
    prompt = build_prompt(query,docs)
    answer = llm(prompt)
    return answer


# In[33]:


query = 'Give me a high protein vegetarian diet'


# In[34]:


#Test
print(rag(query))


# ## Retrieval Evaluation

# In[37]:


evaluate_query = pd.read_csv('data/nutrirag_ground_truth.csv')


# In[38]:


evaluate_query.head()


# In[40]:


ground_truth = evaluate_query.to_dict(orient = 'records')


# In[41]:


ground_truth


# In[47]:


def hit_rate(relevance_total):
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)

def mrr(relevance_total):
    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)


# In[48]:


def evaluate(ground_truth, search_function):
    relevance_total = []

    for q in ground_truth:
        query = q['query']
        relevant_foods = set(q['relevant_foods'].split('|'))
        results = search_function(query)
        relevance = [
            (point.payload['food_name'] in relevant_foods)
            for point in results
        ]

        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total),
    }


# In[51]:


evaluate(ground_truth, search)


# In[ ]:




