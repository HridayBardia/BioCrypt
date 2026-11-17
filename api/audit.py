import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api_audit, AuditRequest

app = FastAPI(title="BioCrypt Audit API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/audit")
@app.post("/audit")
@app.post("/")
async def handler(payload: AuditRequest):
    return await api_audit(payload)
