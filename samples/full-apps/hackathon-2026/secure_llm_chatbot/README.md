# Protegrity AI Developer Edition Hackathon 2026

A secure multi-LLM chat interface with enterprise-grade data protection, role-based access control, and comprehensive audit trails. Built with React and Django, featuring Protegrity PII protection and provider-flexible LLM integrations.

Protegrity AI Developer Edition full app sample.

## Demo video

https://www.youtube.com/watch?v=DcSQH0ZOf3E

## Quick Start

1) Copy env template:

```bash
cp .env.example backend/.env
```

2) Configure at least one LLM provider in `backend/.env`:
- Uncomment one provider block in `.env.example`
- Fill required API credentials for that provider

3) Run:

```bash
./run.sh
```

4) Stop:

```bash
./stop.sh
```

📖 Additional details: [documentation/OVERVIEW.md](documentation/OVERVIEW.md)

---

## Project structure

```text
secure_llm_chatbot/
├── backend/
├── frontend/
├── documentation/
├── run.sh
├── stop.sh
└── requirements.txt
```

## Notes

- This sample runs **inside** the main `protegrity-developer-edition` repo.
- Do not use a nested repo copy inside this directory.
- Docker services are always managed from the repo-root `docker-compose.yml`.

## LLM Provider Configuration (Vendor-neutral)

- You must configure at least one LLM provider in `backend/.env`.
- You can configure multiple providers at once (via `ENABLED_LLM_PROVIDERS` or auto-detection).
- If multiple providers are configured, available models/providers are exposed by backend APIs and can be selected in the app UI.

Quick start:

```bash
cp .env.example backend/.env
```

Then open `backend/.env`, uncomment one provider block, and fill required values.

Common options:

- OpenAI: `OPENAI_API_KEY`
- Azure OpenAI: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` (recommended quick start)
- Anthropic direct: `ANTHROPIC_API_KEY`
- Amazon Bedrock: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`

Start the app:

```bash
./run.sh
```

With zero configured providers, startup fails early with guidance and points to `.env.example`.

## More docs

- [documentation/OVERVIEW.md](documentation/OVERVIEW.md)
- [documentation/backend/RUN.md](documentation/backend/RUN.md)
- [documentation/frontend/RUN.md](documentation/frontend/RUN.md)
