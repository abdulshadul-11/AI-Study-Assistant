

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from groq import Groq

app = FastAPI(
    title="AI Study Assistant API",
    version="1.0.0",
)

MODEL = "openai/gpt-oss-20b"


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    action: str = Field(default="learn", max_length=50)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "AI Study Assistant API is running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ask")
def ask_ai(request: AskRequest):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server API key is not configured."
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    prompts = {
        "learn": "Teach this topic in simple language with an example: ",
        "summary": "Create concise study notes and a summary about: ",
        "quiz": "Create 5 MCQs with four options and answers about: ",
        "flashcards": "Create 6 question-and-answer flashcards about: ",
        "exam": "Give 5 important exam questions about: ",
        "plan": "Create a practical 5-day study plan for: ",
    }

    prompt = prompts.get(
        request.action,
        prompts["learn"]
    ) + question

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI Study Assistant. "
                        "Use clear, student-friendly language. "
                        "Never output HTML."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=700,
        )

        answer = response.choices[0].message.content or ""

        return {
            "answer": answer,
            "action": request.action,
            "model": MODEL,
        }

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI service request failed. Please try again."
        )
