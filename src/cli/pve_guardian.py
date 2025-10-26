import typer
from pathlib import Path
from src.scanner.repo_scanner import scan_repo_and_write_report

app = typer.Typer(help="Proxmox Script Guardian CLI")

@app.command()
def scan_remote(
    repo: str,
    out: str = "report.json",
    ref: str | None = None
):
    """Scan a remote repo (owner/repo or git URL) and save JSON report."""
    outpath = Path(out).expanduser().resolve()
    scan_repo_and_write_report(repo, str(outpath), ref=ref)
    print(f"Wrote report to {outpath}")
