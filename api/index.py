from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class DebateRequest(BaseModel):
    topic: str

def get_response(role: str, topic: str, previous_response: str = "") -> str:
    messages = [
        {"role": "system", "content": f"You are a {role} in a debate. Provide a {'reasonable explanation' if role == 'husband' else 'counter-argument with examples or exceptions to your husband\'s perspective'} on the given topic."},
        {"role": "user", "content": f"Topic: {topic}" + (f"\nHusband's perspective: {previous_response}" if role == "wife" else "")}
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

@app.post("/api/debate")
async def debate(request: DebateRequest):
    try:
        husband_response = get_response("husband", request.topic)
        wife_response = get_response("wife", request.topic, husband_response)
        
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
