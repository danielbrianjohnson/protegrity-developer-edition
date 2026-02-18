# Secure LLM Chatbot — Repository Compliance Plan

## Objective

Restructure this project from its current location under `samples/full-apps/hackathon-2026/secure_llm_chatbot` into a template-compliant, industry-first, feature-tagged example layout **within this project directory only**, without editing repository-level docs or files outside this folder.

## Scope and Constraints

### In Scope

- Files and folders under this path only:
  - `samples/full-apps/hackathon-2026/secure_llm_chatbot/**`
- Creating a local example-repo structure for this project:
  - `catalog/`
  - `examples/`
  - `_templates/`
  - `scripts/`
  - `docs/`
- Moving/reorganizing existing app assets (backend/frontend/scripts/docs) to comply with the template.

### Out of Scope

- Any edits to:
  - repository root `README.md`
  - root `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
  - any path outside `samples/full-apps/hackathon-2026/secure_llm_chatbot`

## Target End State

The project becomes self-contained and template-aligned with this structure:

```text
secure_llm_chatbot/
├── README.md
├── catalog/
│   ├── examples.json
│   ├── features.yml
│   └── industries.yml
├── examples/
│   └── developer-experience/
│       └── protegrity-ai-llm/
│           ├── README.md
│           ├── example.yml
│           ├── .env.example
│           ├── app/
│           │   ├── backend/
│           │   ├── frontend/
│           │   ├── run.sh
│           │   ├── stop.sh
│           │   └── run_tests.sh
│           ├── docs/
│           │   ├── architecture.md
│           │   └── screenshots/   (optional)
│           ├── infra/             (optional)
│           └── data/              (optional, synthetic only)
├── _templates/
│   ├── README_TEMPLATE.md
│   ├── example.yml
│   ├── .env.example
│   └── docker-compose.yml
├── scripts/
│   ├── validate-examples.py
│   └── build-catalog.py
└── docs/
    └── REPO_COMPLIANCE_PLAN.md
```

## Navigation Model (Explicit)

### Primary navigation = Industry/domain

Implementation:

- The first level under `examples/` is the industry slug.
- For this project, the canonical path is:
   - `examples/developer-experience/protegrity-ai-llm/`

How users browse:

- Start at `examples/`
- Pick industry folder (`developer-experience` now; others later like `banking`, `healthcare`, etc.)
- Open the example slug folder

### Secondary navigation = Feature tags

Implementation:

- Canonical feature tags are defined once in `catalog/features.yml`.
- Each example declares tags in `example.yml` under `features:`.
- `catalog/examples.json` is generated from `example.yml` and includes those tags for index/search/filtering.

For this example (`protegrity-ai-llm`), expected feature tags include:

- `data-discovery`
- `pii-redaction`
- `tokenization`
- `semantic-guardrails`
- `auditing-logging`

### Feature Matrix placement

Constraint-aware decision:

- The guideline says root README matrix is optional.
- Because this migration cannot edit root docs, we will place a **local matrix** in:
   - `secure_llm_chatbot/README.md`
   - (optional duplicate) `catalog/examples.json`-derived matrix section in local docs

Result:

- We still satisfy feature-first discovery for this project without violating the no-root-edits rule.

## Implementation Phases

## Phase 1 — Baseline inventory (no functional changes)

1. Capture current file map for backend, frontend, run scripts, and existing docs.
2. Confirm required runtime entry points still identified:
   - `run.sh`
   - `stop.sh`
   - `run_tests.sh`
3. Confirm active env template source:
   - `backend/.env.example`

Deliverable:
- Verified inventory and migration map.

## Phase 2 — Create compliant skeleton

1. Create local folders:
   - `catalog/`, `examples/`, `_templates/`, `scripts/`, `docs/`
2. Seed canonical metadata files:
   - `catalog/features.yml`
   - `catalog/industries.yml`
3. Seed one example path:
   - `examples/developer-experience/protegrity-ai-llm/`

Deliverable:
- Navigable industry-first structure exists in-project.

## Phase 3 — Migrate runnable app into example `app/`

1. Move existing runnable assets into:
   - `examples/developer-experience/protegrity-ai-llm/app/`
2. Preserve relative behavior of startup scripts.
3. Keep any existing docs by relocating to:
   - `examples/developer-experience/protegrity-ai-llm/docs/`

Deliverable:
- Single canonical runnable location under industry/example path.

## Phase 4 — Metadata and README standardization

1. Add `example.yml` with required contract fields:
   - `name`, `slug`, `industry`, `owner`, `difficulty`, `runtime`, `languages`, `features`, `products`, `summary`, `use_case`, `security_notes`
2. Add per-example `.env.example`.
3. Rewrite per-example `README.md` to exact required heading order:
   1. What this example does
   2. Use case
   3. What it demonstrates
   4. Features showcased
   5. Products/components used
   6. Architecture
   7. Getting started
   8. Try it
   9. Security & privacy notes
   10. Troubleshooting
   11. Next steps / extensions
   12. License

Deliverable:
- Example documentation and metadata fully template compliant.

## Phase 5 — Local catalog + validation tooling

1. Add local `_templates/` starter files.
2. Add `scripts/validate-examples.py` checks for:
   - missing `example.yml`
   - missing required README headings
   - slug mismatch (folder vs metadata)
   - feature tags not in canonical list
3. Add `scripts/build-catalog.py` to generate/update `catalog/examples.json`.
4. Run both scripts and fix any findings.

Deliverable:
- Repeatable local quality checks and generated catalog index.

## Compliance Checklist

- [ ] Industry-first path exists: `examples/developer-experience/protegrity-ai-llm/`
- [ ] Feature tags defined once in `catalog/features.yml`
- [ ] Example has `README.md`, `example.yml`, `.env.example`
- [ ] README uses required section order/headings
- [ ] Sensitive config values are env-driven (no hardcoded secrets)
- [ ] Validator passes with no errors
- [ ] Catalog JSON generated from metadata

## Risks and Mitigations

1. **Risk:** Startup scripts break after move.
   - **Mitigation:** Update relative paths in scripts during migration and test run commands.

2. **Risk:** Duplicate app copies create confusion.
   - **Mitigation:** Prefer move (not copy) once new location is validated.

3. **Risk:** Hidden references to old paths in docs or scripts.
   - **Mitigation:** Search within this project folder and patch references before finalizing.

## Acceptance Criteria

This effort is complete when:

- The chatbot runs from the new example path.
- The example metadata is complete and valid.
- The per-example README follows the required template exactly.
- No files outside this project folder were edited.

## Rollback Plan

If migration causes runtime issues:

1. Revert moved paths within this project folder only.
2. Restore original startup script paths.
3. Re-run baseline startup from prior known-good layout.

## Execution Notes

- Keep changes small and phase-based.
- Validate after each phase.
- Do not modify root repository documentation or global policies as part of this migration.
