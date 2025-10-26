import typer
from pathlib import Path
from src.scanner.repo_scanner import scan_repo, scan_repo_and_write_report

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


@app.command()
def scan_local(
    path: str,
    out: str = "report.json"
):
    """Scan a local directory of scripts and save JSON report."""
    outpath = Path(out).expanduser().resolve()
    path = Path(path).expanduser().resolve()
    if not path.is_dir():
        raise typer.BadParameter(f"{path} is not a valid directory")
    
    report = scan_repo(repo="local-scan", repo_path=str(path))
    
    with open(outpath, "w", encoding="utf-8") as fh:
        import json
        json.dump(report, fh, indent=2)
    
    print(f"Wrote report to {outpath}")

