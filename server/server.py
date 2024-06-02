from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from github import get_relevant_code
from pydantic import BaseModel

class GenerateReq(BaseModel):
    url: str

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_guide(req: GenerateReq):
    print(f'Generating guide for {req.url}')

    return {
        "text": get_relevant_code(req.url)
    }
