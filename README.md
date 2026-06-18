# Paper Scout

**Agents hallucinate citations. This one reads the papers first.**

A keyless research-paper finder and verifier. No login, no API key. It finds the work that answers a research question, then proves it by reading the actual papers. It never invents a title or an arXiv ID.

One file. Stdlib Python. No dependencies.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE) · [Listed on Solid State](https://solidstate.cc/skills/paper-scout)

---

## Quick start

No setup, no key, no account.

```bash
python3 scripts/scout.py selftest
```

```
OK — keyless index answered. sample: Attention Is All You Need (https://arxiv.org/abs/1706.03762)  [no key]
```

If it answers, you're done. A free `FIRECRAWL_API_KEY` lifts the per-IP rate limit but is never required.

This repo is an agent skill: point your agent at `SKILL.md`, or run `scripts/scout.py` directly.

## The five moves

**`search`** — semantic search over abstracts. The first move for almost any query.

```bash
python3 scripts/scout.py search "training-free detection of AI-generated text" --k 10
```

**`similar`** — turn one good hit into the rest of its family.

```bash
python3 scripts/scout.py similar arxiv:1706.03762 --mode references --k 15
```

`--mode similar` finds niche siblings, `citers` finds who builds on it, `references` finds what it builds on.

**`inspect`** — canonical metadata for one paper.

```bash
python3 scripts/scout.py inspect arxiv:1706.03762
```

**`read`** — the in-body passages that answer one question. This is how you verify.

```bash
python3 scripts/scout.py read arxiv:2305.17359 "what datasets is the method evaluated on" --k 4
```

**`github`** — issues, PRs, and READMEs. Engineering prior art, not papers.

```bash
python3 scripts/scout.py github "flash attention int8 kv cache" --k 10
```

Every move takes `--json` for piping into the next step.

## What it's for

- **Find the paper**, by name or by method.
- **Map a field.** `similar --mode similar` off a seed builds a real related-work set.
- **Ground a claim.** `read` the paper for the number before a draft asserts it. The anti-hallucination move for any writing agent.
- **Find prior art.** `github` before you build.
- **Scan what's new.** `search "<topic>" --from 2026-01-01` is a field tracker.
- **Build a reading list.** References are the prerequisites, citers are the frontier.

## How it stays honest

- **Never fabricates.** Returns only ids, titles, and numbers the index actually returned. No invented arXiv ids.
- **Reads the score.** Passages come back scored. A low score is treated as unconfirmed, never laundered into a citation.
- **Degrades out loud.** If the index can't answer, `search` falls back to the public arXiv API and says so on stderr. The other moves print the error instead of guessing. Pass `--no-fallback` to fail hard.

## Configuration

The research index answers over plain HTTP with no login and no key, capped per IP per day. The script talks to it directly, so it never depends on a vendor's MCP tools shipping.

| Variable | Default | Purpose |
| --- | --- | --- |
| `FIRECRAWL_API_KEY` | unset | Optional. Lifts the per-IP rate limit. Never gates anything. |
| `PAPER_SCOUT_TIMEOUT` | `30` (90 for `read`) | Request timeout, in seconds. |
| `PAPER_SCOUT_BASE` | Firecrawl research index | Override the backend endpoint. |

## Provenance & license

Solid State original. The data backend is Firecrawl's public research index, accessed over its documented keyless HTTP API. No Firecrawl code, prompts, or branding is reproduced. The skill, method, five-move framing, arXiv fallback, and low-score discipline are written from scratch by Solid State.

MIT, see [LICENSE](./LICENSE). Copy it. Fork it. Ship it.

---

*Cite the literature. Not the vibe. — [Solid State](https://solidstate.cc)*
