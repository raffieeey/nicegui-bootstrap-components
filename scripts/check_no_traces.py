#!/usr/bin/env python3
"""Block generation traces (tool names, watermarks, AI config paths) in the repo.
Repo-local, deterministic, no external dependencies."""

import os
import re
import subprocess
import sys

IDENTITY = [
    r"\bclaude\b",
    r"\bchatgpt\b",
    r"\bopenai\b",
    r"\bgpt-?\d",
    r"\banthropic\b",
    r"\bgrok\b",
    r"\bkimi\b",
    r"\bmoonshot\b",
    r"\bcline\b",
    r"\bdeepseek\b",
    r"\bcopilot\b",
    r"\bcodex\b",
    r"\bgemini\b",
    r"\.cursorrules",
    r"cursor\s+rules",
    r"\.cursor/",
    r"\.clauderc",
    r"\.claude/",
    r"generated\s+(by|with|using)",
    r"co-?authored\s*by",
    r"assisted\s+by",
    r"\bai[- ](assistant|generated|helper|powered|written)\b",
]
IDENTITY_PATHS = [
    r"(^|/)\.cursor(/|$)",
    r"(^|/)\.cursorrules$",
    r"(^|/)\.clauderc$",
    r"(^|/)\.claude(/|$)",
    r"(^|/)CLAUDE\.md$",
    r"(^|/)AGENTS\.md$",
    r"(^|/)\.windsurf(/|$)",
    r"(^|/)\.aider",
    r"(^|/)\.github/copilot",
]
BINARY_EXT = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    ".pdf",
    ".zip",
    ".gz",
    ".mp4",
    ".webm",
}


def ignored_paths(root: str) -> set[str]:
    """Files git ignores can never be published, so they are not audited.

    Keeps the gate aligned with the external pre-push audit: build output and
    caches cannot reach a push, so scanning them only creates false positives
    (e.g. search-index language bundles containing dictionary words).
    """
    result = subprocess.run(
        ["git", "ls-files", "--others", "--ignored", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__ + "/.."))
    ignored = ignored_paths(root)
    fails = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in (".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", "site")
        ]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            rel_posix = rel.replace(os.sep, "/")
            if rel_posix in ignored:
                continue  # untracked and gitignored: cannot reach a push
            if rel_posix == "scripts/check_no_traces.py":
                continue  # policy tool: its own pattern literals are not repo content
            if any(re.search(p, rel) for p in IDENTITY_PATHS):
                fails.append(f"PATH {rel}")
                continue
            if os.path.splitext(fn)[1].lower() in BINARY_EXT:
                continue
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            for pat in IDENTITY:
                m = re.search(pat, text, re.I)
                if m:
                    line = text[: m.start()].count("\n") + 1
                    fails.append(f"{rel}:{line} [{m.group(0)}]")
    if fails:
        for f in fails[:40]:
            print(f"FAIL {f}")
        print(f"{len(fails)} generation-trace findings; commit blocked")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
