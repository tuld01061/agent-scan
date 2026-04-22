from pathlib import Path

from agentscan.discovery import SUPPORTED_SUFFIXES, discover_paths


def test_supported_suffixes_match_v0_1_scope() -> None:
    assert SUPPORTED_SUFFIXES == {".yaml", ".yml", ".json", ".md", ".txt"}


def test_discover_paths_returns_sorted_supported_files(tmp_path: Path) -> None:
    (tmp_path / "b.json").write_text("{}", encoding="utf-8")
    (tmp_path / "a.yaml").write_text("name: demo", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "skip.py").write_text("print('x')", encoding="utf-8")

    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "c.md").write_text("# prompt", encoding="utf-8")

    result = discover_paths(tmp_path)

    assert result == [
        tmp_path / "a.yaml",
        tmp_path / "b.json",
        nested / "c.md",
        tmp_path / "notes.txt",
    ]


def test_discover_paths_accepts_single_supported_file(tmp_path: Path) -> None:
    target = tmp_path / "skill.yml"
    target.write_text("name: agent", encoding="utf-8")

    assert discover_paths(target) == [target]
