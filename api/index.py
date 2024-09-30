from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app = FastAPI()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class DebateRequest(BaseModel):
    topic: str

def get_husband_response(topic: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a husband in a debate. Provide a reasonable explanation on the given topic."},
            {"role": "user", "content": f"Give your perspective as a husband on: {topic}"}
        ]
    )
    return response.choices[0].message.content

def get_wife_response(topic: str, husband_response: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a wife in a debate. Provide a counter-argument with examples or exceptions to your husband's perspective."},
            {"role": "user", "content": f"Topic: {topic}\nHusband's perspective: {husband_response}\nGive your counter-argument:"}
        ]
    )
    return response.choices[0].message.content

@app.post("/api/debate")
async def debate(request: DebateRequest):
    try:
        husband_response = get_husband_response(request.topic)
        wife_response = get_wife_response(request.topic, husband_response)
        
        return {
            "topic": request.topic,
            "husband_response": husband_response,
            "wife_response": wife_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/healthcheck")
async def healthcheck():
    return {"status": "ok"}
