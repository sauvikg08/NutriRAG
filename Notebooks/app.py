from fastapi import FastAPI
from pydantic import BaseModel

from rag import rag

app = FastAPI()

class QuestionRequest(BaseModel):
    question:str

class QuestionResponse(BaseModel):
    question:str
    answer:str

@app.post("/question", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    answer = rag(request.question)

    return QuestionResponse(
        question=request.question,
        answer=answer
    )



