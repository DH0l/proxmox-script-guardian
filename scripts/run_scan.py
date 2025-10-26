#!/usr/bin/env python3
"""
Static scan runner for CI and local runs.
This modifies sys.path so imports work regardless of PYTHONPATH.
Outputs a JSON object with findings per file.
"""
import sys
import os
import glob
import json
from typing import Dict, Any

# Ensure repo root is on sys.path so `from src.analyzer...` works.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Import the analyzer from the package
try:
    from src.analyzer.rules import analyze_script
except Exception:
    # Fallback: try direct import if PYTHONPATH points at src
    from analyzer.rules import analyze_script  # type: ignore

def main() -> None:
    print("Scanning repository scripts...")
    issues: Dict[str, Any] = {}
    for path in glob.glob("**/*.sh", recursive=True):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception as e:
            print(f"Could not read {path}: {e}")
            continue
        findings = analyze_script(content)
        if findings:
            issues[path] = [
                {
                    "line_no": f.line_no,
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "message": f.message,
                }
                for f in findings
            ]

    # Print JSON summary
    print(json.dumps(issues, indent=2))
    if issues:
        print("Warnings found")

if __name__ == "__main__":
    main()
