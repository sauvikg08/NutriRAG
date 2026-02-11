from search import search
from prompt import build_prompt
from llm import llm

def rag(query, limit=5):
    docs = search(query, limit)
    prompt = build_prompt(query,docs)
    answer = llm(prompt)
    return answer