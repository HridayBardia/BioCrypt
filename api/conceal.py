import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api_conceal, ConcealRequest

app = FastAPI(title="BioCrypt Conceal API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/conceal")
@app.post("/conceal")
@app.post("/")
async def handler(payload: ConcealRequest):
    return await api_conceal(payload)
