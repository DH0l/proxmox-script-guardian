import re
from dataclasses import dataclass
from typing import List

@dataclass
class Finding:
    line_no: int
    pattern: str
    message: str

RULES = [
    (re.compile(r"curl\s+.*\|\s*(bash|sh)"), "Piped curl to shell"),
    (re.compile(r"wget\s+.*-O\s*-\s*\|\s*(bash|sh)"), "Piped wget to shell"),
    (re.compile(r"rm\s+-rf\s+/\b"), "Dangerous rm -rf / pattern"),
]

def analyze_script(text: str) -> List[Finding]:
    findings: List[Finding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for pattern, message in RULES:
            if pattern.search(line):
                findings.append(Finding(line_no=i, pattern=pattern.pattern, message=message))
    return findings
