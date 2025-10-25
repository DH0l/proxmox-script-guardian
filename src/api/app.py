from fastapi import FastAPI
from pydantic import BaseModel
from src.analyzer.rules import analyze_script

app = FastAPI(title="Proxmox Script Guardian API")

class AuditRequest(BaseModel):
    content: str

@app.post("/audit")
def audit(req: AuditRequest):
    findings = analyze_script(req.content)
    return {"findings": [f.__dict__ for f in findings]}
