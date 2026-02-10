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