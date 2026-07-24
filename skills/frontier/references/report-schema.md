# Synthesis report contracts

## Default brief

The default output is a concise one-page briefing:

```markdown
# Frontier Brief: <topic>

> As of <date> · covering <window>

## Bottom Line

## Notable Advances

### <Plain-language advancement>

What changed and why it matters, in two or three sentences.

**Evidence:** [paper], [official post], [model/code] · preprint / published / official claim

## Frontier Company Activity

- **<Company>:** one meaningful activity

## What It Adds Up To

## Sources and Caveats
```

Brief rules:

- Include at most five notable advancements.
- Lead with conclusions, not search methodology.
- Use plain language and avoid unnecessary jargon.
- Include only the most useful supporting links.
- Mention metrics only when they materially explain significance.
- Omit empty company sections.
- Mention source failures only when they could change the conclusion.
- Do not include candidate counts, query variants, or full comparison tables.

## Deep report

Use this format only when the user asks for more detail:

```markdown
# Frontier AI: <topic>

## Executive Summary
## Search Scope and Source Health
## Key Technological Advancements
### <Advancement>
## Cross-Advancement Comparison
## Emerging Technical Directions
## Open Questions and Limitations
## References
## Reproducibility Log
```

Each advancement must retain:

- Type: `method`, `model`, `harness`, `tool`, `benchmark`, or `system`.
- Technical contribution.
- Why it matters.
- Supporting paper, company-publication, model-card, repository, and evaluation links.
- Authority and evidence level.
- Limitations and confidence.

Every major synthesized claim must cite supporting URLs. The internal evidence record must distinguish:

- `announced`: a primary source reports the work.
- `supported`: technical evidence is available.
- `independently corroborated`: an external evaluation or reproduction supports it.

Company claims must be attributed. A model card or repository listing does not independently establish performance. The report must label preprints and disclose failed or unavailable source lanes when material.
