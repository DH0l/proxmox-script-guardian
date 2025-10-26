import glob, json
from src.analyzer.rules import analyze_script

print("Scanning repository scripts...")

issues = {}
for path in glob.glob("**/*.sh", recursive=True):
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    findings = analyze_script(content)
    if findings:
        issues[path] = [f.__dict__ for f in findings]

print(json.dumps(issues, indent=2))
if issues:
    print("Warnings found")
