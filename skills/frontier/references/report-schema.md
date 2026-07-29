# Synthesis report contracts

Frontier reports explain what changed in plain language. Research papers and official lab publications remain distinct evidence classes underneath the synthesis; they are not mandatory top-level report lanes.

## Default brief

The default output is a one-page technical note:

```markdown
# <Topic>

> <date window> · <paper count> papers and <lab-post count> lab posts cited

## The short version
## What changed
## Also worth knowing
## What to watch
## Sources and limits
```

Read [writing-style.md](writing-style.md) before drafting.

### The short version

Use two or three sentences. State the main change, what did not change when relevant, and the strongest qualification. Start with the finding; do not describe the report or search process.

### What changed

Include at most three supported changes, ordered by importance. Do not force three. If no candidate clears the evidence threshold, say so plainly.

Each change must include:

- A plain title stating the change
- The supported previous baseline, or `not established`
- What the new evidence shows
- A direct technical or practical consequence, when established
- Supporting links, evidence type, evidence maturity, and confidence
- The strongest material caveat, contradiction, or unknown

Do not describe an isolated company announcement as a broader shift.

### Also worth knowing

Include at most five compact items that matter but do not qualify as principal changes. Use only applicable labels:

- `Research` for a paper finding or technique
- `Deployment` for a concrete lab or engineering move
- `Counter-signal` for evidence that weakens a likely conclusion

Attribute first-party statements and preserve publication status, readiness, evidence level, and external-validation limits in the sentence.

### What this changes

This section is conditional. Include one to three direct implications only when the requested audience benefits from separate guidance. Do not emit default Engineer, Founder, and Investor blocks.

### What to watch

Include at most three specific unresolved questions, evaluations, or developments that could change the current conclusion. Do not use this section as a second caveat list.

### Sources and limits

Keep the brief standalone with a compact footer:

- Count only papers and lab posts actually cited by the brief.
- Name enabled paper indexes, the momentum feed, and lab-site coverage.
- Disclose material failed, partial, rate-limited, or unavailable lanes.
- Omit unconfigured optional providers.

Brief rules:

- Lead with conclusions, not search methodology.
- Follow [writing-style.md](writing-style.md).
- Keep research evidence, company authority, external validation, adoption, and attention distinguishable.
- If X is enabled, summarize social attention separately from technical findings; disclose the effective window, fetched-post cap, trend clusters, and truncation.
- Include only the most useful supporting links.
- Treat Hugging Face ranking and upvotes as momentum context only.
- Treat X views, likes, reposts, replies, bookmarks, impressions, and follower counts as attention context only. A viral post is not a trend, and a trend is not a validated technical result.
- Say when an evidence class or source lane was unavailable; do not imply an unavailable lane had no results.
- Do not include query variants, full comparison tables, or uncited candidate counts.
- Keep the visible brief bounded: three principal changes, five other items, three watch items, and three audience implications when that conditional section is needed.

## Deep report

Use this format only when the user asks for more detail. Deep mode may retain the established research and company lanes:

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
