"""Static analyzer rules for Proxmox Script Guardian.

This module provides a small, test-driven ruleset for detecting risky shell
patterns in helper scripts. Rules are intended to be conservative heuristics
which produce findings that should be reviewed manually.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Finding:
    line_no: int
    rule_id: str
    severity: str
    message: str

# RULES: tuple(rule_id, severity, compiled_regex, message)
# severity: "info", "warning", "danger"
RULES: List[Tuple[str, str, re.Pattern, str]] = [
    ("R001", "danger", re.compile(r"source\s+<\(\s*curl"), "Remote source via curl: executes remote code"),
    ("R002", "danger", re.compile(r"curl\s+.*\|\s*(sh|bash)"), "Piped curl to shell"),
    ("R003", "danger", re.compile(r"wget\s+.*-O\s*-\s*\|\s*(sh|bash)"), "Piped wget to shell"),
    ("R004", "danger", re.compile(r"rm\s+-rf\s+/\b"), "Dangerous rm -rf / pattern"),
    ("R005", "danger", re.compile(r"\bdd\s+if="), "Potential raw disk write with dd"),
    ("R006", "warning", re.compile(r"mkfs\."), "Filesystem creation (mkfs)"),
    ("R007", "warning", re.compile(r"chmod\s+4755"), "SUID bit being set (chmod 4755)"),
    ("R008", "warning", re.compile(r"chmod\s+777"), "World-writable permissions (chmod 777)"),
    ("R009", "warning", re.compile(r"ssh-copy-id|authorized_keys"), "SSH key installation or authorized_keys modification"),
    ("R010", "warning", re.compile(r"base64\s+-d|openssl\s+enc\s+-d"), "Decoding / executing encoded blobs"),
    ("R011", "warning", re.compile(r"apt-key\s+add"), "Adding apt key to system (apt-key add)"),
    ("R012", "warning", re.compile(r"--allow-unauthenticated"), "apt-get install with --allow-unauthenticated"),
    ("R013", "warning", re.compile(r"useradd|adduser|passwd\s"), "User creation or password modification"),
    ("R014", "warning", re.compile(r"systemctl\s+(enable|start|restart|daemon-reload)"), "systemd unit modification / control"),
    ("R015", "warning", re.compile(r"releases/download|\.deb\b|\.rpm\b|\.tar\.gz\b"), "Downloading binary artifacts (inspect for checksums)"),
    ("R016", "info", re.compile(r"curl\s+https?://(raw\.githubusercontent|raw\.github\.com)"), "Fetching raw content from GitHub raw; still check contents"),
]

def analyze_script(text: str) -> List[Finding]:
    """Analyze provided script text and return list of Findings.

    This is intentionally line-based and conservative; false positives are
    possible and findings should be manually inspected.
    """
    findings: List[Finding] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for rule_id, severity, pattern, message in RULES:
            if pattern.search(line):
                findings.append(Finding(line_no=i, rule_id=rule_id, severity=severity, message=message))
    return findings
