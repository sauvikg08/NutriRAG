# NutriRAG
Making healthy food choices is difficult when dietary goals, preferences, and constraints must all be considered at once. People often struggle to balance calories, protein intake, meal types, and food restrictions while planning their daily diet.

NutriRAG provides a Retrieval Augmented Generation(RAG) system that builds personalized diet plans based on user goals, dietary preferences, food availability, and budget. Using a custom nutrition dataset, embeddings retrieval, and an LLM layer, it generates grounded, constraint-aware diet plans that are both personalized and nutritionally transparent.


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




