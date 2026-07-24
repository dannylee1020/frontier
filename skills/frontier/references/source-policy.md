# Frontier source policy

Frontier has two report lanes and one paper-attention overlay.

## Research Frontier

Canonical scholarly providers:

- **OpenAlex:** broad scholarly discovery and publication metadata.
- **arXiv:** recent preprints, especially in computer science, mathematics, physics, and AI.
- **Semantic Scholar:** discovery, abstracts, related metadata, open-access links, and citation signals.

Momentum overlay:

- **Hugging Face Papers:** current attention feed for papers. It is locally topic-filtered and merged by arXiv ID, DOI, or conservative title matching.

Hugging Face rank, upvotes, and feed submission date do not establish technical quality, novelty, or scholarly corroboration. Preserve the paper's publication date separately from `momentum_observed_at`.

## Company Frontier

The host agent searches the approved official research/engineering domains in [company-sources.md](company-sources.md) in parallel with the bundled paper utility. Only substantive research findings, methods, models, evaluations, harnesses, and technical tools qualify.

A company publication is primary evidence that the organization made a claim. It is not independent validation of that claim and must not raise a paper's evidence level.

## Separate insight semantics

- **Research insight:** grounded in a scholarly paper record; may be labeled published, preprint, abstract-level, full-text, or trending on Hugging Face.
- **Company insight:** grounded in an official technical publication; label the organization and attribute claims as first-party.
- **Cross-lane connection:** a thematic or explicit link between the two. Do not collapse the records or count company activity as scholarly corroboration.

## Source status

The report must distinguish `ok`, `partial`, `rate-limited`, `unavailable`, and `error` for each provider or lane. Paper status must distinguish `published`, `preprint`, `submitted`, `corrected`, `retracted`, and `unknown` whenever records support it.

## Partial results

A provider timeout, rate limit, malformed response, unavailable host search, or missing company page is nonfatal. The search artifact and final report must record the failure. A failed source must never be represented as having no results.
