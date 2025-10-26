"""
repo_scanner.py

Small utility to clone a public Git repository (shallow), scan for script files,
and analyze them with the project's static analyzer.

Important safety note:
- This module ONLY reads files. It NEVER executes any code in the target repo.
- It performs a `git clone --depth 1` for speed and minimal network/disk use.
"""

from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
from typing import Dict, Any, List
import glob
import json
import logging

# import the analyzer (works with our repo layout)
try:
    from src.analyzer.rules import analyze_script
except Exception:
    # fallback if PYTHONPATH points at src
    from analyzer.rules import analyze_script  # type: ignore

LOG = logging.getLogger("repo_scanner")
LOG.setLevel(logging.INFO)
if not LOG.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOG.addHandler(ch)


def _shallow_clone(repo: str, ref: str | None = None, dest: str | None = None) -> str:
    """Shallow-clone `repo` into `dest` (or a new tempdir). Returns path to checkout.

    `repo` should be a git URL (ssh or https) or a GitHub shorthand owner/repo.
    `ref` can be a branch or tag name; if not provided we clone default branch.
    """
    # accept GH shorthand "owner/repo"
    if "/" in repo and not repo.startswith(("http://", "https://", "git@")):
        repo_url = f"https://github.com/{repo}.git"
    else:
        repo_url = repo

    cleanup_dest = False
    if dest is None:
        dest = tempfile.mkdtemp(prefix="psg_repo_")
        cleanup_dest = True

    # prepare git clone command
    cmd = ["git", "clone", "--depth", "1", "--no-tags"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [repo_url, dest]

    LOG.info("Cloning %s (ref=%s) -> %s", repo_url, ref, dest)
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # cleanup if clone failed
        if cleanup_dest and os.path.isdir(dest):
            shutil.rmtree(dest, ignore_errors=True)
        raise RuntimeError(f"git clone failed: {e.stderr.decode().strip()}") from e

    return dest


def scan_repo(
    repo: str,
    ref: str | None = None,
    globs: List[str] | None = None,
    repo_path: str | None = None,
    cleanup: bool = True,
) -> Dict[str, Any]:
    """
    Clone `repo` and scan files matching `globs` (default: ["**/*.sh"]).
    Returns a dict: { "repo": repo, "ref": ref, "results": { file_path: [finding, ...], ... } }.

    Parameters:
    - repo: git URL or "owner/repo" shorthand.
    - ref: optional branch or tag.
    - globs: list of glob patterns to match files (relative to repo root).
    - repo_path: optional path to an existing local checkout (skip clone).
    - cleanup: whether to remove the temporary clone when done.
    """
    globs = globs or ["**/*.sh"]
    tmpdir = None
    used_tmpdir = False

    try:
        if repo_path:
            checkout = repo_path
        else:
            tmpdir = _shallow_clone(repo, ref=ref, dest=None)
            checkout = tmpdir
            used_tmpdir = True

        results: Dict[str, Any] = {}
        # iterate over configured globs
        for pattern in globs:
            full_pattern = os.path.join(checkout, pattern)
            # use glob.glob with recursive enabled
            for path in glob.glob(full_pattern, recursive=True):
                # normalize relative path
                rel = os.path.relpath(path, checkout)
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as fh:
                        content = fh.read()
                except Exception as e:
                    LOG.warning("Could not read %s: %s", path, e)
                    continue
                findings = analyze_script(content)
                if findings:
                    # convert dataclass-ish objects to plain dicts if needed
                    results[rel] = [
                        {
                            "line_no": f.line_no,
                            "rule_id": getattr(f, "rule_id", getattr(f, "pattern", "")),
                            "severity": getattr(f, "severity", "warning"),
                            "message": f.message,
                        }
                        for f in findings
                    ]
        return {"repo": repo, "ref": ref, "results": results}
    finally:
        if cleanup and used_tmpdir and tmpdir and os.path.isdir(tmpdir):
            LOG.info("Cleaning up %s", tmpdir)
            shutil.rmtree(tmpdir, ignore_errors=True)


def scan_repo_and_write_report(
    repo: str, outpath: str, ref: str | None = None, **kwargs
) -> str:
    """
    Convenience: run scan_repo and write JSON report to `outpath`.
    Returns outpath.
    """
    report = scan_repo(repo, ref=ref, **kwargs)
    dirpath = os.path.dirname(outpath)
    if dirpath and not os.path.isdir(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    with open(outpath, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    LOG.info("Wrote report to %s", outpath)
    return outpath


# Example quick-run when module executed directly:
if __name__ == "__main__":  # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser(description="Scan a public git repo for risky shell scripts.")
    parser.add_argument("repo", help="Git URL or github owner/repo (eg: community-scripts/ProxmoxVE)")
    parser.add_argument("--ref", help="Branch or tag to checkout", default=None)
    parser.add_argument("--out", help="Write JSON report to this file", default="report.json")
    parser.add_argument("--no-cleanup", help="Don't delete the temporary checkout", action="store_true")
    args = parser.parse_args()
    scan_repo_and_write_report(args.repo, args.out, ref=args.ref, cleanup=not args.no_cleanup)
    print("Done")
