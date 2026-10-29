# Dzongkha Corpus

An open, community-built collection of Dzongkha text (Unicode Dzongkha/Tibetan script) for language technology, linguistic research, and the preservation and wider use of Dzongkha.

> **Status:** v0.1 draft. The repository structure and rules are in place; the corpus is just starting to grow. Contributions are welcome.

## What is in this repository

```
.
├── README.md               This file
├── CONTRIBUTING.md         How to submit text (start here to contribute)
├── LICENSE                 License for code and scripts (MIT)
├── DATA_LICENSE.md         License for corpus data (CC BY-SA 4.0)
├── ATTRIBUTION.md          Credits for third-party sources, including Wikipedia
├── schema/
│   └── record.schema.json  JSON Schema for one corpus record
├── data/
│   ├── samples/            Example records showing the format
│   └── submissions/        Contributed text goes here, one folder per contributor
├── scripts/
│   └── validate.py         Checks submissions (encoding, schema, normalization, duplicates)
├── tests/                  Tests for the checker
├── requirements.txt        Python dependencies for the checker
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/validate.yml   Runs the checks on every pull request
```

## Data format

Each record is one line of a `.jsonl` file with the text and its metadata:

```json
{"id": "dz-sample-0001", "text": "...", "lang": "dz", "script": "Tibt", "source": "...", "domain": "web", "license": "CC-BY-SA-4.0", "contributor_id": "maintainers", "submitted_on": "2026-10-29", "review_status": "pending"}
```

The full field list is in [`schema/record.schema.json`](schema/record.schema.json). See [`data/samples/sample.jsonl`](data/samples/sample.jsonl) for working examples.

## What we accept

- Dzongkha text in Unicode (UTF-8), written by you or that you have the right to share.
- Text that is public domain, under a license compatible with CC BY-SA 4.0 (such as CC BY-SA, CC BY, or CC0), or used with written permission that allows release under CC BY-SA 4.0.

We do **not** accept legacy-font (non-Unicode) text, personal or private data, hateful content, text under NonCommercial or NoDerivatives licenses, or copyrighted material without permission.

## How to contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md). You can contribute through a pull request on GitHub, or, if you do not use Git, through the submission form or by opening an issue (see the guide).

## Automated checks

Every pull request is checked automatically (UTF-8, JSON, schema, NFC normalization, Dzongkha-script characters, duplicates, Wikipedia license rules, and folder and file names). You can run the same checks on your computer:

```bash
pip install -r requirements.txt
python scripts/validate.py
```

The checks cannot tell Dzongkha from Classical Tibetan, so a fluent reviewer still approves every submission.

## Licenses

- **Corpus data:** [CC BY-SA 4.0](DATA_LICENSE.md). Please credit "The Dzongkha Corpus Project contributors" and share any adaptations under the same license.
- **Code and scripts:** [MIT](LICENSE).

The corpus includes text from Dzongkha Wikipedia, which is licensed under CC BY-SA; this is why the whole corpus uses the same license. Wikipedia and other third-party sources are credited in [ATTRIBUTION.md](ATTRIBUTION.md) and in each record's `source`, `source_url`, `revision_id`, and `license` fields.

## Takedown requests

If you are a rights holder or an individual and want something removed, contact **[tandin.cst@gm....com]**. Removed items are excluded from all later releases.

## Citing

A citation entry and a DOI will be added with the first Zenodo release.

## Contact

Maintainers: **[Tandin and Karma]**
