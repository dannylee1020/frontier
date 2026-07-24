# Synthesis report contracts

## Default brief

The default output is a concise one-page briefing with two independent insight lanes:

```markdown
# Frontier Brief: <topic>

> As of <date> · covering <window>

## Bottom Line

## Research Frontier

### <Paper insight>

What changed and why it matters.

**Evidence:** preprint / published / abstract-level / full-text / trending on Hugging Face

## Company Frontier

### <Company publication insight>

What the organization reported and why it matters.

## What Connects Them

## Sources and Caveats
```

Brief rules:

- Include at most three Research Frontier items and three Company Frontier items.
- Rank the two lanes independently.
- Lead with conclusions, not search methodology.
- Use plain language and avoid unnecessary jargon.
- Include only the most useful supporting links.
- Mention metrics only when they materially explain significance.
- Attribute company claims explicitly.
- Treat Hugging Face ranking and upvotes as momentum context only.
- Say when a lane was unavailable; do not imply an unavailable lane had no results.
- Do not include candidate counts, query variants, or full comparison tables.

## Deep report

Use this format only when the user asks for more detail:

```markdown
# Frontier AI: <topic>

## Executive Summary
## Search Scope and Source Health
## Research Frontier
### <Paper insight>
## Company Frontier
### <Company insight>
## What Connects Them
## Open Questions and Limitations
## References
## Reproducibility Log
```

Each insight must retain internally:

- Insight type: `research` or `company`
- Technical contribution
- Why it matters
- Supporting paper or official-publication links
- Authority and evidence level
- Hugging Face momentum metadata for research insights, when present
- Limitations and confidence

Every major synthesized claim must cite supporting URLs. The internal evidence record must distinguish `announced`, `supported`, and `independently corroborated`. Company claims must be attributed. The report must label preprints and disclose failed or unavailable source lanes when material.
