# Technical artifact contract

Artifacts are technical records discovered alongside papers. They are not coerced into paper records.

Supported types:

- `model`: a Hugging Face model and its associated model card.
- `repository`: a GitHub repository containing a model, tool, harness, benchmark, or implementation.
- `company_publication`: an official technical research or engineering post found by host-native, site-restricted search.

Each artifact should preserve:

- Stable identifier and canonical URL
- Artifact type and title
- Owner or organization
- Publication/creation and update dates
- Description or technical summary
- License when available
- Tags, language, and relevant metadata
- Authority classification
- Evidence level
- Related paper, model, repository, and benchmark URLs

Authority classifications:

- `primary-official`: first-party artifact from the named organization or its verified namespace.
- `verified-owner`: repository/model owner is verified but the artifact is not necessarily first-party research.
- `community`: third-party artifact.
- `unknown`: provenance could not be established.

Evidence levels:

- `metadata-only`: listing metadata only.
- `card-or-readme`: model card or repository README was inspected.
- `full-text`: linked technical documentation or implementation was inspected.

Popularity signals such as stars, downloads, and likes may be shown as context but must not be used as evidence of technical quality or novelty.
