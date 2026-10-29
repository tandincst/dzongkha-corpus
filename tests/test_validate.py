import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402

GOOD = "ཐིམ་ཕུ་འདི་འབྲུག་གི་རྒྱལ་ས་ཨིན།"
OTHER = "བཀའ་དྲིན་ཆེ།"


def record(n=1, cid="tester", text=GOOD, **over):
    rec = {
        "id": f"dz-{cid}-{n:04d}",
        "text": text,
        "lang": "dz",
        "script": "Tibt",
        "source": "original writing",
        "domain": "other",
        "license": "CC-BY-SA-4.0",
        "contributor_id": cid,
        "submitted_on": "2026-10-29",
        "review_status": "pending",
    }
    rec.update(over)
    return rec


def write(root, cid, name, records):
    path = root / "submissions" / cid / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    return path


def check(root):
    issues, _ = validate.run([root], data_root=root)
    errors = [i.message for i in issues if i.level == "error"]
    warnings = [i.message for i in issues if i.level == "warning"]
    return errors, warnings


def has(messages, fragment):
    return any(fragment in m for m in messages)


def test_valid_submission_passes(tmp_path):
    write(tmp_path, "tester", "2026-10-29-basic.jsonl", [record(1), record(2, text=OTHER)])
    errors, warnings = check(tmp_path)
    assert errors == [] and warnings == []


def test_not_nfc_is_an_error(tmp_path):
    # U+0F73 is not in NFC form (it decomposes to U+0F71 U+0F72)
    write(tmp_path, "tester", "2026-10-29-nfc.jsonl", [record(text="ཀ\u0f73་ཀ་ཀ།")])
    errors, _ = check(tmp_path)
    assert has(errors, "NFC")


def test_latin_only_text_is_an_error(tmp_path):
    write(tmp_path, "tester", "2026-10-29-latin.jsonl", [record(text="Hello world.")])
    errors, _ = check(tmp_path)
    assert has(errors, "no Tibetan letters")


def test_disallowed_character_is_an_error(tmp_path):
    write(tmp_path, "tester", "2026-10-29-emoji.jsonl", [record(text=GOOD + " 😀")])
    errors, _ = check(tmp_path)
    assert has(errors, "outside Tibetan script")


def test_duplicate_text_across_files_is_an_error(tmp_path):
    write(tmp_path, "tester", "2026-10-29-a.jsonl", [record(1)])
    write(tmp_path, "tester", "2026-10-30-b.jsonl", [record(2)])
    errors, _ = check(tmp_path)
    assert has(errors, "duplicate text")


def test_duplicate_id_is_an_error(tmp_path):
    write(tmp_path, "tester", "2026-10-29-a.jsonl", [record(1), record(1, text=OTHER)])
    errors, _ = check(tmp_path)
    assert has(errors, "duplicate id")


def test_wikipedia_text_needs_cc_by_sa_and_revision(tmp_path):
    rec = record(license="CC-BY-4.0", source_url="https://dz.wikipedia.org/wiki/Example")
    write(tmp_path, "tester", "2026-10-29-wiki.jsonl", [rec])
    errors, _ = check(tmp_path)
    assert has(errors, "CC-BY-SA-4.0")
    assert has(errors, "revision_id")


def test_contributor_must_match_folder(tmp_path):
    write(tmp_path, "tester", "2026-10-29-mismatch.jsonl", [record(contributor_id="someone")])
    errors, _ = check(tmp_path)
    assert has(errors, "must match the folder name")


def test_missing_required_field_is_an_error(tmp_path):
    rec = record()
    del rec["source"]
    write(tmp_path, "tester", "2026-10-29-missing.jsonl", [rec])
    errors, _ = check(tmp_path)
    assert has(errors, "source")


def test_permission_granted_needs_reference(tmp_path):
    write(tmp_path, "tester", "2026-10-29-perm.jsonl", [record(license="permission-granted")])
    errors, _ = check(tmp_path)
    assert has(errors, "permission_ref")


def test_bad_file_name_is_an_error(tmp_path):
    write(tmp_path, "tester", "My File.jsonl", [record()])
    errors, _ = check(tmp_path)
    assert has(errors, "file name must look like")


def test_invalid_utf8_is_an_error(tmp_path):
    path = tmp_path / "submissions" / "tester" / "2026-10-29-bad.jsonl"
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"text": "\xff\xfe"}\n')
    errors, _ = check(tmp_path)
    assert has(errors, "not valid UTF-8")


def test_missing_shad_is_only_a_warning(tmp_path):
    write(tmp_path, "tester", "2026-10-29-warn.jsonl", [record(text="བཀའ་དྲིན་ཆེ")])
    errors, warnings = check(tmp_path)
    assert errors == []
    assert has(warnings, "shad")
