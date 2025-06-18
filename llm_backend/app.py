from fastapi import FastAPI
from pydantic import BaseModel
from llama_cpp import Llama
import os

model_path = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

llm = Llama(model_path=model_path)

app = FastAPI()

class Query(BaseModel):
    prompt: str
    max_tokens: int = 512

@app.post("/generate")
def generate(query: Query):
    response = llm(
        query.prompt,
        max_tokens=query.max_tokens
    )
    return {"response": response["choices"][0]["text"]}