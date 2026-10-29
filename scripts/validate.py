#!/usr/bin/env python3
"""Validate Dzongkha corpus files (.jsonl).

Usage:
    python scripts/validate.py                  # check everything under data/
    python scripts/validate.py PATH [PATH ...]  # check specific files or folders
    python scripts/validate.py --strict         # treat warnings as errors

The exit code is 1 if any error is found (or any warning with --strict).
In GitHub Actions, problems are shown as annotations on the pull request.

What is checked
    Errors (must be fixed):
      - file is valid UTF-8, one JSON object per line
      - every record matches schema/record.schema.json
      - text is NFC-normalized
      - text uses only Tibetan script, digits, spaces and basic punctuation
        (a few Latin letters are allowed; mostly-Latin text is rejected)
      - no duplicate text or duplicate record IDs
      - Wikipedia text has license CC-BY-SA-4.0, a source_url and a revision_id
      - files in data/submissions follow the folder and file name rules and
        contributor_id matches the folder name
    Warnings (a reviewer will look at them):
      - no tsheg in longer text, text not ending in a shad, Latin letters,
        spaces at the start or end, blank lines

Limitation: this script cannot tell Dzongkha from Classical Tibetan. A fluent
reviewer must still check the language of every submission.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata
from collections import namedtuple
from pathlib import Path
from urllib.parse import urlparse

try:
    import jsonschema
except ImportError:  # pragma: no cover
    sys.exit("Missing dependency. Run: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = ROOT / "data"
SCHEMA_PATH = ROOT / "schema" / "record.schema.json"

Issue = namedtuple("Issue", "level path line message")

# Allowed outside the Tibetan block: space, newline, ASCII digits and basic punctuation.
ALLOWED_PUNCT = set(" \n.,;:!?()[]\"'-/%\u2013\u2014\u2026\u201c\u201d\u2018\u2019")
# Characters a sentence may end with: shad, double shad, and common closing punctuation.
END_CHARS = set("\u0f0d\u0f0e.!?\u201d\")")
TSHEG = "\u0f0b"
NB_TSHEG = "\u0f0c"
FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9_-]*\.jsonl$")
MAX_LATIN_SHARE = 0.2


def is_tibetan(ch: str) -> bool:
    return 0x0F00 <= ord(ch) <= 0x0FFF


def describe(ch: str) -> str:
    if unicodedata.category(ch) == "Cc":
        return f"U+{ord(ch):04X} control character"
    return f"U+{ord(ch):04X} {unicodedata.name(ch, 'UNNAMED')}"


def check_text(text: str) -> list[tuple[str, str]]:
    """Return (level, message) pairs for one text value."""
    issues: list[tuple[str, str]] = []

    if unicodedata.normalize("NFC", text) != text:
        issues.append(("error", "text is not NFC-normalized; fix with unicodedata.normalize('NFC', text)"))

    tibetan_letters = 0
    latin_letters = 0
    bad: list[str] = []
    for ch in text:
        if is_tibetan(ch):
            if unicodedata.category(ch) == "Lo":
                tibetan_letters += 1
            continue
        if ch in ALLOWED_PUNCT or (ch.isascii() and ch.isdigit()):
            continue
        if ch.isalpha() and "LATIN" in unicodedata.name(ch, ""):
            latin_letters += 1
            continue
        d = describe(ch)
        if d not in bad:
            bad.append(d)

    if bad:
        shown = "; ".join(bad[:5]) + (" ..." if len(bad) > 5 else "")
        issues.append(("error", f"text has characters outside Tibetan script and basic punctuation: {shown}"))

    if tibetan_letters == 0:
        issues.append(("error", "text contains no Tibetan letters"))
    elif latin_letters / (tibetan_letters + latin_letters) > MAX_LATIN_SHARE:
        issues.append(("error", "text is mostly Latin letters, not Dzongkha"))
    elif latin_letters:
        issues.append(("warning", f"text contains {latin_letters} Latin letter(s); check that they belong"))

    if tibetan_letters >= 6 and TSHEG not in text and NB_TSHEG not in text:
        issues.append(("warning", "no tsheg (\u0f0b) between syllables; check the text is correctly typed"))

    stripped = text.strip()
    if stripped != text:
        issues.append(("warning", "text has spaces or newlines at the start or end"))
    if tibetan_letters and stripped and stripped[-1] not in END_CHARS:
        issues.append(("warning", "text does not end with a shad (\u0f0d) or other sentence-ending mark"))

    return issues


def relative_to(path, base):
    try:
        return Path(path).resolve().relative_to(Path(base).resolve())
    except ValueError:
        return None


def display_path(path) -> str:
    rel = relative_to(path, ROOT)
    return rel.as_posix() if rel is not None else str(path)


def collect_files(paths, issues):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and not f.name.startswith("."):
                    files.append(f)
        elif p.is_file():
            files.append(p)
        else:
            issues.append(Issue("error", p, 0, "path does not exist"))
    return files


def run(paths, data_root=DATA_ROOT, schema_path=SCHEMA_PATH):
    """Validate paths. Returns (issues, stats)."""
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    submissions = Path(data_root) / "submissions"
    samples = Path(data_root) / "samples"

    issues: list[Issue] = []
    seen_text: dict[str, tuple[Path, int]] = {}
    seen_id: dict[str, tuple[Path, int]] = {}
    n_files = n_records = 0

    for f in collect_files(paths, issues):
        sub_rel = relative_to(f, submissions)
        in_samples = relative_to(f, samples) is not None

        def add(level, line, message, f=f):
            issues.append(Issue(level, f, line, message[:300]))

        if f.suffix != ".jsonl":
            if sub_rel is not None:
                add("error", 0, "only .jsonl files are accepted in data/submissions")
            continue

        n_files += 1
        if sub_rel is not None:
            if len(sub_rel.parts) != 2:
                add("error", 0, "file must be at data/submissions/<contributor-id>/<YYYY-MM-DD>-<topic>.jsonl")
            elif not FILENAME_RE.match(sub_rel.parts[1]):
                add("error", 0, "file name must look like YYYY-MM-DD-topic.jsonl (lowercase letters, digits, - and _)")

        raw = f.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            add("error", 1, "file starts with a byte order mark (BOM); save as UTF-8 without BOM")
            raw = raw[3:]
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            add("error", 0, f"file is not valid UTF-8 (problem at byte {e.start})")
            continue

        lines = content.split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        if not lines:
            add("warning", 0, "file is empty")

        for i, line in enumerate(lines, 1):
            line = line.rstrip("\r")
            if not line.strip():
                add("warning", i, "blank line")
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                add("error", i, f"invalid JSON: {e.msg} (column {e.colno})")
                continue
            if not isinstance(rec, dict):
                add("error", i, "each line must be a JSON object")
                continue
            n_records += 1

            for err in sorted(validator.iter_errors(rec), key=lambda e: [str(p) for p in e.absolute_path]):
                loc = ".".join(str(p) for p in err.absolute_path)
                add("error", i, f"schema: {loc + ': ' if loc else ''}{err.message}")

            text = rec.get("text")
            if isinstance(text, str):
                for level, msg in check_text(text):
                    add(level, i, "text: " + msg)
                if not in_samples:
                    key = unicodedata.normalize("NFC", text).strip()
                    if key in seen_text:
                        prev, prev_line = seen_text[key]
                        add("error", i, f"duplicate text (also at {display_path(prev)}:{prev_line})")
                    else:
                        seen_text[key] = (f, i)

            rid = rec.get("id")
            if isinstance(rid, str):
                if rid in seen_id:
                    prev, prev_line = seen_id[rid]
                    add("error", i, f"duplicate id {rid!r} (also at {display_path(prev)}:{prev_line})")
                else:
                    seen_id[rid] = (f, i)

            submitted = rec.get("submitted_on")
            if isinstance(submitted, str):
                try:
                    dt.date.fromisoformat(submitted)
                except ValueError:
                    add("error", i, f"submitted_on {submitted!r} is not a real date (use YYYY-MM-DD)")

            url = rec.get("source_url")
            host = ""
            if isinstance(url, str):
                parsed = urlparse(url)
                host = (parsed.hostname or "").lower()
                if parsed.scheme not in ("http", "https") or not host:
                    add("error", i, "source_url must be a full http(s) link")
            source = rec.get("source")
            if host.endswith("wikipedia.org") or (isinstance(source, str) and "wikipedia" in source.lower()):
                if rec.get("license") != "CC-BY-SA-4.0":
                    add("error", i, "Wikipedia text must have license CC-BY-SA-4.0")
                if not url:
                    add("error", i, "Wikipedia text needs source_url (permanent link to the article)")
                if not rec.get("revision_id"):
                    add("error", i, "Wikipedia text needs revision_id")

            if sub_rel is not None and len(sub_rel.parts) == 2:
                folder = sub_rel.parts[0]
                cid = rec.get("contributor_id")
                if cid != folder:
                    add("error", i, f"contributor_id {cid!r} must match the folder name {folder!r}")
                elif isinstance(rid, str) and not rid.startswith(f"dz-{cid.lower()}-"):
                    add("warning", i, f"id {rid!r} should start with 'dz-{cid.lower()}-'")

    return issues, {"files": n_files, "records": n_records}


def _escape(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def emit(issue: Issue, github: bool) -> None:
    path = display_path(issue.path)
    if github:
        level = "error" if issue.level == "error" else "warning"
        line = f",line={issue.line}" if issue.line else ""
        print(f"::{level} file={path}{line}::{_escape(issue.message)}")
    else:
        where = f"{path}:{issue.line}" if issue.line else path
        print(f"{issue.level.upper():7} {where}: {issue.message}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate Dzongkha corpus .jsonl files.")
    parser.add_argument("paths", nargs="*", help="files or folders to check (default: data/)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    paths = args.paths or [DATA_ROOT]
    issues, stats = run(paths)

    github = os.environ.get("GITHUB_ACTIONS") == "true"
    for issue in issues:
        emit(issue, github)

    errors = sum(1 for i in issues if i.level == "error")
    warnings = sum(1 for i in issues if i.level == "warning")
    print(f"\nChecked {stats['files']} file(s), {stats['records']} record(s): "
          f"{errors} error(s), {warnings} warning(s).")
    if errors or (args.strict and warnings):
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
