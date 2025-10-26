# Proxmox Script Guardian

Proxmox Script Guardian is a static analysis tool for scanning Proxmox helper scripts and other shell scripts for risky patterns. It is designed to be safe—scripts are **never executed**—and provides a structured report of potentially dangerous code.

---

## Features

- Scans shell scripts in local directories or remote Git repositories.
- Detects risky operations like piped `curl | bash`, `rm -rf /`, SUID changes, filesystem modifications, and more.
- Outputs findings in JSON with line numbers, rule IDs, and severity levels (`info`, `warning`, `danger`).

---

## Getting Started

### Prerequisites

- Python 3.11+
- `git`
- Virtual environment recommended

### Install

```
git clone https://github.com/DH0l/proxmox-script-guardian.git
cd proxmox-script-guardian
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Usage

#### Scan a remote Git repository

```
python -m src.cli.pve_guardian scan-remote community-scripts/ProxmoxVE --out /tmp/remote_report.json
```

This clones the repo (shallow, depth 1) and produces a JSON report.

#### Scan a local directory

```
python -c "
from pathlib import Path
from src.scanner.repo_scanner import scan_repo
import json

report = scan_repo(repo='local-test', repo_path=str(Path.home()/'test-scripts'))
with open('/tmp/test_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('Wrote report to /tmp/test_report.json')
"
```

---

## Ruleset Overview

The analyzer detects common risky patterns, including:

| Rule ID | Severity | Description |
|---------|---------|-------------|
| R001    | danger  | Remote source via `curl` |
| R002    | danger  | Piped `curl | bash` |
| R004    | danger  | `rm -rf /` patterns |
| R005    | danger  | Raw disk write (`dd if=`) |
| R006-R016 | warning/info | Other potential system modifications or suspicious commands |

For a full list, see `src/analyzer/rules.py`.

---

## Testing

```
pytest tests/
```

The tests validate the ruleset and ensure new rules produce expected findings.

---

## Notes

- Only performs static analysis. Review all findings manually.
- Designed for Proxmox helper scripts but can be used on any shell scripts.
