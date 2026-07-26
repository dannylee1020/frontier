# Official frontier-lab sources

Frontier tracks substantive official publications from the following organizations. Use the host agent's native web search in parallel with the bundled paper search, restricting each query to the listed domains and paths.

| Organization | Preferred technical paths | Notes |
|---|---|---|
| Anthropic | `anthropic.com/research`, `anthropic.com/engineering` | Research findings, evaluations, agent and safety engineering, and material capability direction.
| OpenAI | `openai.com/research`, `openai.com/index` | Research, technical reports, model and system findings, and substantive capability releases.
| Google DeepMind | `deepmind.google/blog` | Research, models, science, safety, and technical system direction.
| Meta | `ai.meta.com/blog`, `research.facebook.com` | AI research, open-model findings, systems, and evaluations.
| Microsoft | `microsoft.com/en-us/research/blog` | Research, engineering findings, infrastructure, and developer systems.
| NVIDIA | `research.nvidia.com`, `developer.nvidia.com/blog` | Models, systems, hardware/software, inference research, and deployment tooling.
| Kimi / Moonshot AI | `kimi.com/blog`, `moonshot.ai` | Kimi model, agent, training, serving research, and technical releases.
| Qwen | `qwenlm.github.io/blog`, `qwen.ai/research` | Qwen technical posts, model reports, evaluations, and capability releases.
| GLM / Z.ai | `z.ai`, `docs.z.ai` | Official GLM research, model findings, technical documentation, and releases.
| DeepSeek | `api-docs.deepseek.com/news`, `api-docs.deepseek.com/updates` | Official technical model and API publications; verify research claims against linked reports or papers.

## Search contract

For a topic such as `long-context agents`, use site-restricted queries such as:

```text
site:anthropic.com/research OR site:anthropic.com/engineering "long-context agents"
site:openai.com/research OR site:openai.com/index "long-context agents"
```

Search result pages are candidate records. The host agent must inspect selected pages before making a claim.

## Inclusion policy

Include an official publication when it reports or reveals at least one of:

- New model, architecture, algorithm, training, or inference method
- New agent or harness design
- New benchmark, evaluation, safety, or deployment result
- Substantive empirical finding
- Technical tool or implementation that enables a new capability
- Capability release that materially changes what is available
- Infrastructure or developer-platform move with technical significance
- Repeated technical priority that provides a credible strategic signal

Classify the selected publication by contribution: `research`, `engineering`, `capability_release`, `infrastructure`, `evaluation`, or `strategic_signal`.

A company publication is a company or lab move even when it is not research. It becomes evidence for a broader landscape direction only when supported by repeated activity, multiple organizations, independent research, external validation, or adoption.

## Exclusion policy

Exclude general company news, partnerships without technical consequences, funding, hiring, generic thought leadership, marketing without technical substance, and ordinary availability announcements. Do not omit a technically substantive release merely because it is also a product announcement.

A company publication is authoritative evidence that the organization made a claim or took an action. It is not independent validation of that claim.
