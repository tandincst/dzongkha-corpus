# Contributing to the Dzongkha Corpus

Thank you for helping build a Dzongkha corpus. Everyone who writes, reads, or teaches Dzongkha can help, whether or not you use GitHub.

## Ways to contribute

- **Submit text** (the main way).
- **Review** submissions for language quality and metadata. Fluent Dzongkha speakers are especially needed.
- **Report problems**: wrong text, wrong metadata, or content that should not be here (open an issue).
- **Improve tools and docs**: scripts, checks, and translations of these guides into Dzongkha.

## What you can submit

Submit text only if **at least one** of these is true:

1. You wrote it yourself.
2. It is in the public domain or under an open license compatible with CC BY-SA 4.0 (for example CC BY-SA, CC BY, or CC0). Licenses with NonCommercial (NC) or NoDerivatives (ND) terms are not compatible.
3. You have written permission from the rights holder (for example a publisher, media house, or institution). The permission must allow release under CC BY-SA 4.0. Keep it and give its reference in `permission_ref`.

Do **not** submit:

- Copyrighted material without permission, even if it is freely readable online.
- Text under NonCommercial (NC) or NoDerivatives (ND) licenses.
- Personal data or private messages, or anything that identifies a private individual.
- Hateful, abusive, or sexually explicit content.
- Text in old non-Unicode fonts (it shows as garbage in Unicode). Convert it first and check the result.
- Machine-generated text, unless clearly labelled in `source`.

## Text requirements

- UTF-8 encoding, written in Dzongkha/Tibetan script (Unicode block U+0F00–U+0FFF).
- NFC-normalized text.
- Syllables separated by the *tsheg* (་) and sentences ended with the *shad* (།).
- One record per sentence, or per short passage, with no personal data.

## The record format

Records are stored as JSON Lines (`.jsonl`): one JSON object per line. Required fields:

| Field | Description |
|---|---|
| `id` | Unique ID, e.g. `dz-yourid-0001` |
| `text` | The Dzongkha text |
| `lang` | Always `dz` |
| `script` | Always `dzo` |
| `source` | Where the text comes from (title, URL, or "original writing") |
| `domain` | `news`, `literature`, `education`, `legal`, `religious`, `encyclopedia`, `web`, or `other` |
| `license` | `CC-BY-SA-4.0` (default for your own writing), `CC-BY-4.0`, `CC0-1.0`, `public-domain`, or `permission-granted` |
| `contributor_id` | Your ID (a username or pseudonym, not your real name unless you choose) |
| `submitted_on` | Date, `YYYY-MM-DD` |
| `review_status` | Set to `pending` |

Optional fields: `author_publisher`, `year`, `source_url`, `revision_id`, and `permission_ref` (required if the text is from a third party under permission). The full definition is in [`schema/record.schema.json`](schema/record.schema.json), and working examples are in [`data/samples/sample.jsonl`](data/samples/sample.jsonl).

## Check your file before submitting

A checker runs automatically on every pull request. You can run it on your computer first:

```bash
pip install -r requirements.txt
python scripts/validate.py
```

With no arguments it checks everything under `data/`, which also catches text that is already in the corpus. To check one file, give its path:

```bash
python scripts/validate.py data/submissions/<your-id>/<YYYY-MM-DD>-<topic>.jsonl
```

The checker reports two kinds of problems:

- **Errors** must be fixed before your pull request can be merged: invalid UTF-8 or JSON, missing or wrong fields, text that is not NFC-normalized, characters outside Tibetan script and basic punctuation, mostly-Latin text, duplicate text or IDs, a wrong folder or file name, and Wikipedia text without the `CC-BY-SA-4.0` license, `source_url`, and `revision_id`.
- **Warnings** are looked at by a reviewer: no *tsheg* in longer text, text that does not end with a *shad*, a few Latin letters, and spaces at the start or end of the text.

The checker cannot tell Dzongkha from Classical Tibetan, so a fluent reviewer still checks the language of every submission. If you do not use Git (Option B), you do not need to run it; a maintainer will.

## Using Wikipedia or other CC BY-SA text

Wikipedia text is licensed under CC BY-SA, which is compatible with this corpus. If you submit it, set `license` to `CC-BY-SA-4.0`, set `domain` to `encyclopedia`, and fill in `source` (article title), `source_url` (permanent link), and `revision_id`. Take text only, not images or quoted material under other licenses. Wikipedia is credited in [ATTRIBUTION.md](ATTRIBUTION.md).

## Option A: Submit with GitHub

1. **Fork** this repository.
2. Add a file at `data/submissions/<your-contributor-id>/<YYYY-MM-DD>-<short-topic>.jsonl`.
3. Run the checker (see "Check your file before submitting") and fix any errors.
4. Open a **pull request**. Fill in the checklist in the pull request template.
5. A reviewer will comment. Fix anything they raise; once approved, a maintainer will merge it.

## Option B: Submit without GitHub

- Use the submission form: **[form link coming soon]**, or
- Open an issue titled "Submission: <topic>" and paste or attach your text with the source and license information, or
- Email **[tandin.cst@gm....com]**.

A maintainer will convert your submission into the record format and credit you as the contributor.

## Review process

Every submission is checked for encoding and format, duplicates, metadata, and rights. At least one reviewer must approve it before it enters a release. Reviewers may ask for changes or decline a submission that does not meet these rules, and they will explain why.

## Licensing and your rights

By submitting, you confirm that you wrote the text or have the right to share it. Your own writing is released under [CC BY-SA 4.0](DATA_LICENSE.md): others may reuse and adapt it, including commercially, if they credit the project and share adaptations under the same license. Third-party text keeps the license stated in its record. You will be credited in the contributors list.

You can ask for your contribution to be removed at any time, and it will be excluded from later releases. Creative Commons licenses cannot be withdrawn for copies already distributed, so removal does not apply to earlier downloads.

## Behavior

Be respectful and welcoming. We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) as our code of conduct. Report concerns to **[tandin.cst@gm....com]**.

## Questions

Open an issue with the label `question`, or contact the maintainers listed in the README.
