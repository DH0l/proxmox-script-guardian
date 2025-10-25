import typer
import requests
import json

app = typer.Typer()

@app.command()
def audit_local(path: str):
    """Audit a local script file using the local API server"""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    resp = requests.post("http://localhost:8000/audit", json={"content": content})
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    app()
