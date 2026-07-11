#!/usr/bin/env python3
"""Fail when removed legacy canvas identifiers remain in tracked text files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FORBIDDEN = {
    "experimental profile identifier": re.compile(r"experimental-400x480", re.I),
    "legacy portrait canvas": re.compile(r"400\s*[x×]\s*480", re.I),
    "legacy landscape notation": re.compile(r"480\s*[x×]\s*400", re.I),
}
TEXT_SUFFIXES = {
    ".c", ".cs", ".css", ".fprj", ".html", ".js", ".json",
    ".md", ".py", ".txt", ".xml", ".yaml", ".yml",
}


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if (
            path.is_file()
            and ".git" not in path.parts
            and path.name != Path(__file__).name
            and path.suffix.lower() in TEXT_SUFFIXES
        ):
            yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    findings: list[str] = []
    for root in args.paths:
        if not root.exists():
            findings.append(f"missing scan path: {root}")
            continue
        for path in iter_files(root):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for line_number, line in enumerate(text.splitlines(), 1):
                for label, pattern in FORBIDDEN.items():
                    if pattern.search(line):
                        findings.append(
                            f"{path}:{line_number}: {label}: {line.strip()}"
                        )

    if findings:
        print("Legacy canvas references found:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1
    print("No removed legacy canvas references found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
