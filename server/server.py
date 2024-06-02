from fastapi import FastAPI
from github import get_relevant_code
from pydantic import BaseModel

class GenerateReq(BaseModel):
    url: str

app = FastAPI()

@app.post("/generate")
async def generate_guide(req: GenerateReq):
    print(f'Generating guide for {req.url}')
    
    return {
        "text": get_relevant_code(req.url)
    }
