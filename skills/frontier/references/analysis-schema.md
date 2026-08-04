# Analysis contracts

Frontier keeps source evidence records separate and combines them only at the synthesized `frontier_move` layer.

## Research insight

Each paper analysis must include:

- `insight_type`: `research`
- Stable paper reference
- Research question
- Method
- Dataset or evaluation
- Main findings
- Novel contribution
- Prior baseline, or `not established`
- Novelty status: `established`, `claimed`, or `not-established`
- Technical readiness: `exploratory`, `reproducible`, `deployed`, or `unknown`
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
- `momentum-discovered`: found through the momentum feed but not returned by an enabled scholarly provider.

Momentum is attention context, not evidence quality or independent corroboration.

Do not fill missing methodological details from assumptions or from a related paper.

## X social-momentum insight

An X trend record describes retrieved attention, not technical truth. It must include:

- `insight_type`: `x_trend`
- `retrieval_method`: `official-api` or `web-indexed-x`
- Title and matched discovery branches
- First and last observed timestamps
- Post count and unique-author count
- Momentum label and trend type: `viral-post`, `discussion`, `emerging-discussion`, or `single-post`
- Evidence state: `unreviewed`, `artifact-linked`, or `x-only`
- Representative post URLs and linked artifacts
- Limitations, including API cap, web-indexing limits, truncation, and attention-versus-credibility warnings

Views, likes, reposts, replies, bookmarks, impressions, recency, and follower counts are attention metadata. They cannot establish credibility, consensus, adoption, or independent corroboration. A canonical linked artifact must be inspected separately.

## Company and lab-activity insight

Each official publication analysis must include:

- `insight_type`: `company`
- Company and publication title
- `publication_type`: one of:
  - `research`
  - `engineering`
  - `capability_release`
  - `infrastructure`
  - `evaluation`
  - `strategic_signal`
- Technical contribution, release, implementation, or priority
- Previous baseline, or `not established`
- Why it matters
- Authority: `first-party`
- Evidence level: `metadata-only` or `full-text`
- Claim state: `announced`, `supported`, or `independently corroborated`
- External validation, if any
- Related papers, if explicitly linked
- Limitations and unestablished claims
- Confidence
- Supporting URLs

A company publication is authoritative evidence that the organization made a claim or took an action. It is not independent validation of performance or general truth.

## Frontier move

A frontier move is a synthesis of one or more separately analyzed records. It must include:

- `insight_type`: `frontier_move`
- Stable move reference and title
- `move_type`: one of:
  - `research_advance`
  - `engineering_advance`
  - `evaluation_finding`
  - `capability_release`
  - `infrastructure_move`
  - `strategic_signal`
- Previous baseline
- What changed
- Novelty or directional significance
- Supporting evidence records
- Contradictory or limiting evidence
- Landscape effect
- Practical readiness: `exploratory`, `reproducible`, `deployed`, or `unknown`
- Confidence
- Limitations
- Unknowns
- Supporting URLs

A move may connect a paper and a company publication thematically, but their evidence authority and validation states remain separate. A company publication cannot become scholarly corroboration merely by being linked to a paper.

## Claim states

The internal record must distinguish:

- `announced`: a primary source reports the work or action.
- `supported`: technical evidence is available at the recorded evidence level.
- `independently corroborated`: an external evaluation or reproduction supports it.

A company claim cannot become `independently corroborated` merely because it is official. A Hugging Face momentum signal cannot change a claim state.
