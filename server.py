import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="AI Email Support System")

# Connect to local Ollama instance
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama', 
)
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1")

class GenerateRequest(BaseModel):
    incoming_email: str

class EvaluateRequest(BaseModel):
    incoming_email: str
    generated_reply: str

def load_dataset():
    if not os.path.exists("dataset.json"):
        return []
    with open("dataset.json", "r") as f:
        return json.load(f)

dataset_cache = load_dataset()

@app.get("/api/emails")
def get_emails():
    return {"emails": dataset_cache}

@app.post("/api/generate")
def generate_response(req: GenerateRequest):
    few_shot_examples = dataset_cache[:2]
    system_prompt = (
        "You are a professional, empathetic, and helpful customer support agent. "
        "Your job is to draft replies to incoming customer emails. "
        "Do not invent new policies or false promises. Keep it concise but polite.\n\n"
        "Here are some examples of the tone and style we expect:\n"
    )
    for ex in few_shot_examples:
        system_prompt += f"\nIncoming Email: {ex['incoming_email']}\n"
        system_prompt += f"Response:\n{ex['reference_reply']}\n"
        system_prompt += "-" * 20 + "\n"
        
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Incoming Email:\n{req.incoming_email}\n\nPlease generate a response."}
            ],
            temperature=0.7,
        )
        return {"reply": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate")
def evaluate_response(req: EvaluateRequest):
    evaluation_prompt = """
You are an expert customer support manager evaluating AI-generated replies.
Evaluate the Generated Reply based on the Incoming Email on three criteria (scale 1 to 5):
- Relevance (1-5): Does the reply directly address the core issue/question?
- Tone (1-5): Is the reply professional, polite, and empathetic?
- Accuracy (1-5): Does the reply avoid hallucinations (making up policies, features, etc.)?

Respond ONLY with a valid JSON object matching this schema exactly:
{
    "relevance_score": int,
    "tone_score": int,
    "accuracy_score": int,
    "reasoning": "A short 1-2 sentence explanation for the scores."
}
"""
    user_prompt = f"Incoming Email: {req.incoming_email}\nGenerated Reply: {req.generated_reply}\n"
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": evaluation_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        raw_eval = response.choices[0].message.content.strip()
        return json.loads(raw_eval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for the frontend
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
