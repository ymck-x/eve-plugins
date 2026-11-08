from pathlib import Path


def test_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "eve-plugin.yaml").is_file()
    assert (root / "plugin.py").is_file()
