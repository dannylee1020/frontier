# Analysis contracts

Frontier keeps Research Frontier and Company Frontier analyses separate.

## Research insight

Each paper analysis must include:

- `insight_type`: `research`
- Stable paper reference
- Research question
- Method
- Dataset or evaluation
- Main findings
- Novel contribution
- Limitations
- Publication status
- Evidence level
- Hugging Face momentum status, if present
- Confidence
- Unknowns
- Supporting URLs

Evidence levels:

- `metadata-only`: title, author, venue, date, or identifiers only.
- `abstract-level`: the paper abstract or equivalent paper summary was available and supports the statement.
- `full-text`: an accessible paper was actually read.

Hugging Face momentum labels:

- `not_observed`
- `trending-on-huggingface`
- `momentum-discovered`: found through the momentum feed but not returned by a canonical scholarly provider.

Momentum is attention context, not evidence quality or independent corroboration.

Do not fill missing methodological details from assumptions or from a related paper.

## Company insight

Each official publication analysis must include:

- `insight_type`: `company`
- Company and publication title
- `publication_type`: `research`, `engineering`, or `technical_release`
- Technical contribution
- Why it matters
- Authority: `first-party`
- Evidence level: `metadata-only` or `full-text`
- Related papers, if explicitly linked
- Limitations and unestablished claims
- Confidence
- Supporting URLs

A company publication is authoritative evidence that the organization made the claim. It is not independent validation of performance or general truth.

## Claim states

The internal record must distinguish:

- `announced`: a primary source reports the work.
- `supported`: technical evidence is available at the recorded evidence level.
- `independently corroborated`: an external evaluation or reproduction supports it.

A company claim cannot become `independently corroborated` merely because it is official. A Hugging Face momentum signal cannot change a claim state.
