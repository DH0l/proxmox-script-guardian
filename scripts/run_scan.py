#!/usr/bin/env python3
"""
Static scan runner for CI and local runs.
This modifies sys.path so imports work regardless of PYTHONPATH.
"""
import sys
import os
import glob
import json

# Ensure repo root is on sys.path so `from src.analyzer...` works.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Now import the analyzer via the src package
from src.analyzer.rules import analyze_script

def main():
    print("Scanning repository scripts...")
    issues = {}
    for path in glob.glob("**/*.sh", recursive=True):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception as e:
            print(f"Could not read {path}: {e}")
            continue
        findings = analyze_script(content)
        if findings:
            issues[path] = [f.__dict__ for f in findings]

    print(json.dumps(issues, indent=2))
    if issues:
        print("Warnings found")

if __name__ == "__main__":
    main()
