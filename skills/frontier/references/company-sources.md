# Official technical publication sources

Frontier tracks official technical publications from the following organizations. Use the host agent's native web search in parallel with the bundled paper search, restricting each query to the listed domains and paths.

| Organization | Preferred technical paths | Notes |
|---|---|---|
| Anthropic | `anthropic.com/research`, `anthropic.com/engineering` | Research findings, evaluations, agent and safety engineering.
| OpenAI | `openai.com/research`, `openai.com/index` | Research, technical reports, model and system findings.
| Google DeepMind | `deepmind.google/blog` | Research, models, science, and safety.
| Meta | `ai.meta.com/blog`, `research.facebook.com` | AI research and open-model findings.
| Microsoft | `microsoft.com/en-us/research/blog` | Research and engineering findings.
| NVIDIA | `research.nvidia.com`, `developer.nvidia.com/blog` | Models, systems, hardware/software, and inference research.
| Kimi / Moonshot AI | `kimi.com/blog`, `moonshot.ai` | Kimi model, agent, training, and serving research.
| Qwen | `qwenlm.github.io/blog`, `qwen.ai/research` | Qwen technical posts, model reports, and evaluations.
| GLM / Z.ai | `z.ai`, `docs.z.ai` | Official GLM technical documentation and model findings.
| DeepSeek | `api-docs.deepseek.com/news`, `api-docs.deepseek.com/updates` | Official technical model and API announcements; verify research claims against linked reports or papers.

## Search contract

For a topic such as `long-context agents`, use site-restricted queries such as:

```text
site:anthropic.com/research OR site:anthropic.com/engineering "long-context agents"
site:openai.com/research OR site:openai.com/index "long-context agents"
```

Search result pages are candidate records. The host agent must inspect selected pages before making a claim.

## Inclusion policy

Include a company publication when it reports at least one of:

- New model, architecture, algorithm, training, or inference method
- New agent or harness design
- New benchmark or evaluation result
- Substantive empirical finding
- Technical tool or implementation that enables a new capability

Exclude general company news, partnerships, funding, hiring, product marketing, and ordinary availability announcements.

A company publication is authoritative evidence that the organization made a claim. It is not independent validation of that claim.
