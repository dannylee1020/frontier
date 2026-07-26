# Synthesis report contracts

Frontier reports are organized around material changes to the AI frontier. Research papers and official lab publications remain distinct evidence classes underneath the synthesis; they are not mandatory top-level report lanes.

## Default brief

The default output is a concise briefing with this structure:

```markdown
# Frontier Brief: <topic>

> As of <date> · covering <window>

## Bottom Line
## Frontier Shifts
## New Techniques and Findings
## Lab and Deployment Moves
## Landscape Direction
## Implications
## Watchlist and Caveats
```

### Frontier Shifts

Include at most three principal shifts. Each shift should state:

- Previous baseline
- What changed
- Supporting evidence and evidence maturity
- Confidence
- Why the change matters

Do not describe an isolated company announcement as an industry shift. Use `not established` when the prior baseline or landscape effect cannot be supported.

### New Techniques and Findings

Include at most five research-led items. Explain the novel contribution, evaluation, readiness, limitations, and why it matters. Label papers as published, preprint, abstract-level, full-text, or otherwise appropriate.

### Lab and Deployment Moves

Include at most three substantive company or lab moves. These may include research, engineering, capability releases, infrastructure, evaluations, or strategic signals. Attribute first-party claims explicitly and state the degree of external validation.

### Landscape Direction

Summarize convergence, divergence, and strengthening or weakening research and deployment directions. Distinguish a repeated organizational bet from an industry-wide shift.

### Implications

When the audience is not specified, provide compact implications for:

- Engineers
- Founders
- Investors

Tailor the section to the requested persona when known. Do not turn technical evidence into unsupported market forecasts.

### Watchlist and caveats

Include material limitations, contradictions, unknowns, source failures, unvalidated claims, and developments worth monitoring.

Brief rules:

- Lead with conclusions, not search methodology.
- Keep research evidence, company authority, external validation, adoption, and attention distinguishable.
- Include only the most useful supporting links.
- Treat Hugging Face ranking and upvotes as momentum context only.
- Say when an evidence class or source lane was unavailable; do not imply an unavailable lane had no results.
- Do not include candidate counts, query variants, or full comparison tables.

## Deep report

Use this format only when the user asks for more detail:

```markdown
# Frontier AI: <topic>

## Executive Summary
## Search Scope and Source Health
## Frontier Shifts
### <Shift>
#### Previous Baseline
#### New Research
#### Lab and Deployment Activity
#### Supporting and Contradictory Evidence
#### Technical Limitations
## New Techniques and Findings
## Implications
## Open Questions and Limitations
## References
## Reproducibility Log
```

Each synthesized shift must retain internally:

- Stable move type and title
- Previous baseline
- What changed and why it is significant
- Supporting research and company records
- Evidence level and claim state
- Contradictory evidence and limitations
- Practical readiness
- Confidence
- Supporting URLs

Each underlying record must retain:

- Evidence class: `research` or `company`
- Technical contribution
- Authority and evidence level
- Publication status for papers
- Hugging Face momentum metadata for research records, when present
- External validation and limitations

Every major synthesized claim must cite supporting URLs. The internal evidence record must distinguish `announced`, `supported`, and `independently corroborated`. Company claims must be attributed. The report must label preprints and disclose failed or unavailable source lanes when material.
