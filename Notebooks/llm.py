import google.generativeai as genai
genai.configure()
model = genai.GenerativeModel("gemini-2.5-flash")

def llm(prompt):

    response = model.generate_content(prompt)
    return response.text