import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
MODEL_PATH = "/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
llm = None

if os.path.exists(MODEL_PATH):
    from llama_cpp import Llama
    llm = Llama(model_path=MODEL_PATH)

class Query(BaseModel):
    prompt: str
    max_tokens: int = 512

@app.post("/generate")
def generate(query: Query):
    if llm is None:
        return {"response": "(Model not available yet. Please try again later.)"}
    output = llm(query.prompt, max_tokens=query.max_tokens)
    return {"response": output["choices"][0]["text"]}