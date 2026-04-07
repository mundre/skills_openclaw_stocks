"""Auto-generated smoke test."""

def test_skill_directory_exists():
    from pathlib import Path
    assert Path(r"/tmp/browser-ops").exists()
