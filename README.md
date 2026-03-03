# NutriRAG
Making healthy food choices becomes complex when dietary goals, preferences, and constraints must all be considered simultaneously. People often struggle to balance calories, protein intake, meal types, and food restrictions while planning their daily diet.

NutriRAG provides a Retrieval Augmented Generation(RAG) system that builds personalized diet plans based on user goals and dietary preferences. Using a custom nutrition dataset, embeddings retrieval, and an LLM layer, it generates grounded, constraint-aware diet plans that are both personalized and nutritionally transparent.


## Overview

NutriRAG is a RAG application designed to help users with planning their meals based on nutritional requirements.
It allows users to ask questions such as:
* “Build me a high protein non-veg dinner”

* “Create a vegetarian diet plan”

* “Give me low calorie snack options”

The system retrieves relevant food items from a structured nutrition database and generates a diet plan grounded strictly in retrieved data.

## Dataset:

The nutrition dataset used in NutriRAG consists of 103 food items with the following information on them:

* food_name – Name of the food item.
* food_type – Dietary classification (e.g., veg, non-veg).
* serving_size – Standard portion size used for nutritional calculations.
* meal_type – Typical meal category (breakfast, lunch, dinner, snacks).
* calories_kcal – Total energy provided per serving (in kilocalories).
* protein_g – Amount of protein per serving (in grams).
* carbs_g – Total carbohydrates per serving (in grams).
* fats_g – Total fat content per serving (in grams).
* saturated_fat_g – Saturated fat content per serving (in grams).
* monounsaturated_fat_g – Monounsaturated fat content per serving (in grams).
* polyunsaturated_fat_g – Polyunsaturated fat content per serving (in grams).
* trans_fat_g – Trans fat content per serving (in grams).
* fiber_g – Dietary fiber content per serving (in grams).
* sodium_mg – Sodium content per serving (in milligrams).
* calcium_mg – Calcium content per serving (in milligrams).
* phosphorus_mg – Phosphorus content per serving (in milligrams).

The dataset is synthetically generated / LLM-assisted.
The purpose of the dataset is to demonstrate the RAG workflow (ingestion → retrieval → filtering → ranking → generation), not to provide medically accurate dietary advice.

**Disclaimer**: Nutritional values should not be interpreted as clinical recommendations.

In a production system, this pipeline would operate on a validated nutrition database.

Key intent: Show RAG system design, not nutrition correctness.

## Technologies

* Python 3.12.1
* Qdrant for data retrieval
* FastAPI as API Interface
* Google Gemini as LLM

## Preparation:

The project was prepared in codespaces under VSCode. 
To use Qdrant for retrieval, a file `run_qdrant.sh` was created. 
The file had the required steps for starting the qdrant application:
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant_storage:/qdrant/storage" \
    qdrant/qdrant
```
This was run in the beginning using:
```bash
chmod +x run_qdrant.sh

```
followed by
```bash
./run_qdrant.sh
```
For Google Gemini, an  API key was created and entered into the environment using:
```bash
export GOOGLE_API_KEY='your_key'
```
## Ingestion:
Data was embeded using `BAAI/bge-small-en-v1.5`and stored in Qdrant database. Model selection was based on Embedding Dimensionality an ability to understand and vectorise English language.

The field  `food_name` has been vectorised and the fields `meal_type` and `food_type` have been indexed for filtering. 


## Retrieval

The retrieval pipeline follows a two-stage ranking strategy to ensure both semantic relevance and nutritional correctness.

1. Query Understanding & Filtering
User queries are first parsed to extract structured intent signals such as dietary type (veg/non-veg), meal category (breakfast/lunch/dinner), and nutritional constraints (protein, calories, sodium). These signals determine metadata-level filtering before ranking.

2. Two-Stage Ranking Pipeline

Semantic Recall (Embedding-Based Retrieval)
Vector search is used to retrieve semantically relevant food items using embedding similarity.

Nutrition-Aware Re-Ranking (Metadata-Based Scoring)
Since embeddings capture semantic meaning but not numeric magnitude, nutritional fields (e.g., protein_g, calories_kcal, sodium_mg) are not embedded.
Retrieved candidates are re-ranked using actual numeric metadata to ensure results are nutritionally accurate (e.g., highest protein, lowest calories).

This hybrid approach ensures results are contextually relevant and quantitatively correct, which is critical for diet planning systems.


During development, a subtle bug was identified where "veg" matched "non veg" due to substring-based intent parsing.

This caused incorrect filtering (veg results for non-veg queries).

The issue was resolved by token-aware intent extraction and prioritizing more specific terms (non-veg before veg).

## Prompting and Generation

The generation layer uses a strictly controlled prompt template to ensure reliable, structured, and grounded outputs. The LLM is instructed to act as a professional dietician and generate responses only from the retrieved food items, preventing hallucination or fabricated nutrition values. Retrieved entries are dynamically injected into the prompt using a structured entry_template, exposing both semantic fields (food name, meal type, food type) and precise numeric metadata (calories, protein, fats, carbs, micronutrients).

The model is guided with explicit output rules: list each food item separately, include detailed nutrition breakdown per item, compute a total nutrition summary, and organize results by meal type when required. It is also explicitly restricted from referencing internal mechanisms or external sources.

This controlled prompt design ensures the final response is grounded, accurate to the dataset, consistently formatted, and production-ready, making the system suitable for real-world diet planning use cases.

## Evaluation

Retrieval quality was evaluated using:

* Hit Rate - 0.93

* Mean Reciprocal Rank (MRR) - 0.97

Ground truth queries were manually curated for constraint-aware evaluation. This was done to avoid circular evaluation and to reflect realistic user intent. Given the small dataset and intent-driven nature of diet queries, this approach provides clearer and more trustworthy evaluation signals

## API Layer
The system exposes its functionality through a lightweight FastAPI-based REST API, enabling the RAG pipeline to be accessed programmatically. A `/question` POST endpoint accepts a structured request containing the user’s query and returns a JSON response with both the original question and the generated answer.

Pydantic models (QuestionRequest and QuestionResponse) are used for strict input and output validation, ensuring type safety and consistent response structure. The endpoint internally invokes the rag() function, which orchestrates retrieval, re-ranking, prompt construction, and generation.

This API layer cleanly separates the inference logic from the application interface, making the system modular, deployable, and ready for integration with front-end applications or external services.

# How to Run

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Run Qdrant

```bash
chmod +x run_qdrant.sh

```
followed by
```bash
./run_qdrant.sh
```
3. Ingest data (Must be run before starting the API)

```bash
python ingestion.py
```
4. Set Gemini API Key

```bash
export GOOGLE_API_KEY='your_api_key'
```
5. Start API
```bash
uvicorn app:app --reload
```
6. Visit 
```bash
http://127.0.0.1:8000/docs
```

## Limitations
* Dataset is synthetic and limited in size
* No hybrid + dense retrieval

**Note:** 
Generation is constrained retrieved context and explicitly disallows external knowledge, reducing hallucination risk by design rather than post-hoc evaluation. Hence, generation evaluation techniques such as LLM as a Judge have not been implemented.

## Future Improvements

* Hybrid Search (BM25+dense)
* Real World nutrition database ingestion
* Budget aware diet planning
* LLM-as-a-judge evaluation layer






