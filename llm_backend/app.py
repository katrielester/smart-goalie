import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
MODEL_PATH = "/models/active-model.gguf"

from llama_cpp import Llama
llm = Llama(model_path=MODEL_PATH)

# Warm-up to speed up first real generation
llm("Warm up prompt", max_tokens=1)

class Query(BaseModel):
    prompt: str
    max_tokens: int = 512

@app.post("/generate")
def generate(query: Query):
    if llm is None:
        return {"response": "(Model not available yet.)"}

    try:
        output = llm(
            query.prompt, 
            max_tokens=query.max_tokens,
            stop=["\n\n"])
        return {"response": output["choices"][0]["text"]}
    except Exception as e:
        print("Error:", str(e))
        return {"response": f"(Error generating response: {str(e)})"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)