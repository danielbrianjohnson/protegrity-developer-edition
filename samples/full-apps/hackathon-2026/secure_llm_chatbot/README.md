# Protegrity AI Developer Edition — Example Applications (Secure LLM Chatbot Scope)

This folder is organized as an example-repo-style showcase for the Secure LLM Chatbot sample, aligned to industry-first navigation and feature-tagged discovery.

The runnable example is packaged under `examples/<industry>/<example-slug>` and uses metadata plus catalog files so additional examples can be added consistently.

---

## How this project is organized

Primary navigation is by industry/domain, then by example slug:

```text
examples/
	developer-experience/
		protegrity-ai-llm/
			README.md
			example.yml
			.env.example
			app/
			docs/
			data/
			infra/
```

Secondary navigation is by feature tags, defined once in `catalog/features.yml` and referenced by each `example.yml`.

---

## Quick start (run this example)

1) Go to the example folder

```bash
cd examples/developer-experience/protegrity-ai-llm
```

2) Copy env vars

```bash
cp .env.example app/backend/.env
```

3) Run

```bash
cd app
./run.sh
```

4) Open

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000

---

## Examples catalog

### Developer Experience / Platform

- **Protegrity AI (LLM)** (`examples/developer-experience/protegrity-ai-llm`)  
	Full-stack secure chatbot with Protegrity data discovery, redaction, tokenization controls, and semantic guardrails around LLM requests and responses.

---

## Browse by feature

| Feature / Capability | Examples |
|---|---|
| Data discovery | Protegrity AI (LLM) |
| PII redaction | Protegrity AI (LLM) |
| Tokenization / Detokenization | Protegrity AI (LLM) |
| Semantic guardrails | Protegrity AI (LLM) |
| Auditing / logging | Protegrity AI (LLM) |

Tip: See `catalog/examples.json` and `examples/**/example.yml` for machine-readable metadata.

---

## Conventions

- Slugs are kebab-case.
- Every example includes `README.md`, `example.yml`, and `.env.example`.
- No real customer data in the sample; use synthetic/demo data only.
- Secrets are never committed; use environment variables.

---

## Supporting docs

- Plan: `docs/REPO_COMPLIANCE_PLAN.md`
- Example details: `examples/developer-experience/protegrity-ai-llm/README.md`
