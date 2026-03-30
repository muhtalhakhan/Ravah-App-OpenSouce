# Codebase Gap Analysis and Execution TODO

## Purpose
This document tracks:
1. The difference between the current implementation and the intended product from:
   - `docs/ravah-ideation.pdf`
   - `docs/launch-strategy-ravah.pdf`
   - `docs/ideas-ravah.pdf`
2. A step-by-step execution checklist with completion marks.

## Product Intent (What It Should Be)
The intended product is an **AI-powered content generator for founders** that:
- Takes product idea and short description input.
- Captures brand voice (keywords, tone, example post).
- Imports design identity from Figma (logo, colors, typography).
- Generates a 1-week platform-specific content plan (LinkedIn, X, Instagram).
- Produces post outputs (captions, hooks, hashtags, simple visuals).
- Supports export/share to workflows (for example Buffer/Notion later).
- Supports launch flow assets (landing/waitlist funnel and content strategy support).

### New User Flow (from flow diagram)
1. Waitlist user receives **magic link** email.
2. Magic link → **Welcome screen**.
   - If password not set → **Set password screen** → navigate to onboarding.
   - If password already set → go directly to **onboarding flow**.
3. **Onboarding flow** (multi-step):
   - About v0 (intro/explanation step)
   - Input project name
   - Input project description
   - Select brand voice
   - Select social platforms (LinkedIn, X, Instagram)
4. After onboarding complete → **Dashboard**.
   - If onboarding not completed → return to Welcome screen.

### New Architecture (from architecture diagram)
- **Profile/Tone** intake: accepts `csv`, `txt`, `pdf` uploads → processed by **Knowledge Manager**.
- **Knowledge Manager** feeds into **Agent** as an Agent Function.
- **Vector DB** stores Context+Tone embeddings; Agent reads/writes it for retrieval.
- **Agent → API (OpenRouter/Claude)**: Claude preferred for content generation; OpenRouter as current LLM router.
- **Content output**: Text, Visuals, etc.
- **Past Generations/Context** saved to a new DB table; User History must be maintained.

## Current Codebase (What It Is Today)
Current app is a **generic full-stack starter**:
- Auth: signup/login/me.
- Generic CRUD for `items`.
- Generic agent query/status endpoint and page.
- Generic homepage and pages not specialized for founder content generation workflow.

## Gap Matrix (Current vs Required)

### 1) Domain Model
- Current:
  - `User`, domain models added (ProductIdea, BrandProfile, BrandAsset, ContentPlan, ContentPost).
- Required (new):
  - `GenerationHistory` table (past generations + context per user).
  - User onboarding state flag (`onboarding_completed` on `User`).
- Gap: **Medium** (new table + flag needed)

### 2) Backend API
- Current:
  - `/auth/*` (JWT username/password), `/workflow/*` endpoints added.
- Required:
  - **Magic link auth** (replace/supplement password login): send magic link, verify token, set-password flow.
  - File upload endpoint for brand profile ingestion (`csv`, `txt`, `pdf`).
  - Knowledge Manager service (parse uploaded files → extract tone/keywords).
  - Generation history endpoints (save + retrieve past generations per user).
  - Export endpoints (MVP JSON/CSV).
- Gap: **High** (magic link + file upload + history are net-new)

### 3) Agent Logic
- Current:
  - Structured prompting, typed payloads, platform rules, mock fixtures (Phase 3 complete).
- Required (new):
  - **Knowledge Manager** Agent Function: ingest csv/txt/pdf, extract brand voice context.
  - **Vector DB integration**: embed and store Context+Tone; retrieve relevant context per generation.
  - **OpenRouter** as LLM router (Claude preferred for content generation).
  - Persist generation outputs to `GenerationHistory` table.
- Gap: **High** (Vector DB + Knowledge Manager + OpenRouter are net-new)

### 4) Frontend UX
- Current:
  - Home (updated), login/signup, onboarding page (partial), waitlist page stub.
- Required (from flow diagram):
  - **Welcome screen** (post magic-link landing).
  - **Set password screen** (for first-time users).
  - **Onboarding wizard** (5 steps: about v0, project name, project description, brand voice, social platforms). Existing page needs to match these exact steps.
  - **Dashboard** (post-onboarding destination).
  - **Weekly plan screen**.
  - **Generated posts review + edit screen**.
  - **Export screen** (JSON/CSV).
- Gap: **High**

### 5) Launch-Strategy Features
- Current:
  - Waitlist page stub added. No capture backend.
- Required:
  - Waitlist landing page v1 (hero, teaser, email capture CTA).
  - V2 sections (social proof, referral CTA placeholders).
  - Waitlist data capture endpoint + storage.
  - Basic analytics events.
- Gap: **Medium-High**

### 6) Infrastructure
- Current:
  - PostgreSQL, Redis, Docker Compose, GitHub Actions CI.
- Required (new):
  - **Vector DB** (e.g., pgvector extension on existing Postgres, or separate Qdrant/Weaviate service).
  - File storage for uploaded brand assets (`csv`, `txt`, `pdf`).
- Gap: **Medium** (pgvector is low-friction if using existing Postgres)

### 7) Quality and Runtime Health
- Current:
  - 8 passing smoke tests. crewai pin issue in full install.
- Required:
  - Tests for all new workflow APIs.
  - Frontend integration tests for core user flow.
  - Updated README/quickstart.
- Gap: **Medium**

## Execution TODO (Track and Mark)
Use `[x]` when done.

### Phase 0: Stabilize Current Base
- [x] Fix agent import paths (`app.agents.*` -> actual module paths).
  - 2026-03-11: Updated factory and agent modules to import from `app.*` module locations.
- [x] Fix login API contract mismatch (frontend + backend agree on form/json).
  - 2026-03-11: Backend login now accepts JSON payload (`LoginRequest`) matching frontend API client.
- [x] Ensure test tooling works (install/test config) and add a smoke test for auth + agent status.
  - 2026-03-11: Installed core test dependencies, added auth+agent smoke test, and `python -m pytest -q` passes (8 tests).
  - Note: full `requirements.txt` install still fails on pinned `crewai==0.1.26` for this environment.
- [x] Verify backend startup and frontend API integration locally.
  - 2026-03-11: Backend app import/startup check passed with SQLite env; login contract confirmed between frontend and backend.

### Phase 1: Replace Generic `Items` with Product Domain
- [x] Design and add DB models: `ProductIdea`, `BrandProfile`, `BrandAsset`, `ContentPlan`, `ContentPost`.
  - 2026-03-12: Added SQLAlchemy models for founder domain workflow with user-linked relationships.
- [x] Create/adjust schemas for these domain entities.
  - 2026-03-12: Added Pydantic schemas for create/update/response payload shapes for each domain entity.
- [x] Add migrations for new tables.
  - 2026-03-12: Added Alembic script location scaffolding and baseline revision `20260312_0001` to create domain tables.
- [x] Deprecate or remove generic `items` flow.
  - 2026-03-12: Removed `Item` model/schema/router and unmounted `/items` route from backend app.

### Phase 2: Core Founder Workflow APIs
- [x] Add endpoint to create/update product idea.
  - 2026-03-12: Added `POST /workflow/product-ideas` and `PUT /workflow/product-ideas/{idea_id}`.
- [x] Add endpoint to create/update brand voice profile.
  - 2026-03-12: Added `POST /workflow/brand-profile` and `PUT /workflow/brand-profile`.
- [x] Add endpoint to ingest Figma asset metadata (MVP: manual token/file/URL metadata, no deep sync).
  - 2026-03-12: Added `POST /workflow/brand-assets/ingest` for metadata payload capture.
- [x] Add endpoint to generate weekly content plan.
  - 2026-03-12: Added `POST /workflow/content-plans/generate` (draft weekly plan creation).
- [x] Add endpoint to generate platform-specific posts.
  - 2026-03-12: Added `POST /workflow/content-posts/generate` with per-platform draft post outputs.

### Phase 3: Agent Specialization
- [x] Implement structured prompting for founder context + brand voice.
  - 2026-03-12: Added structured founder-content prompt builder in base agent with context fields (product, tone, keywords, platforms).
- [x] Return typed/structured payloads (not only plain string response).
  - 2026-03-12: Extended `/agent/query` response with typed `structured` payload (themes + platform posts + applied rules).
- [x] Add platform-specific rules (LinkedIn/X/Instagram tone and length constraints).
  - 2026-03-12: Added per-platform constraints and enforcement in agent generation pipeline.
- [x] Add deterministic mock fixtures for local testing.
  - 2026-03-12: Added deterministic fixtures and hashing-based stable output generation for repeatable tests.

### Phase 4: Auth Flow — Magic Link + Welcome + Set Password
- [ ] Add magic link send endpoint (`POST /auth/magic-link`) — generates token, emails user.
- [ ] Add magic link verify endpoint (`GET /auth/magic-link/verify?token=...`) — validates token, returns session.
- [ ] Add set-password endpoint (`POST /auth/set-password`) for first-time users.
- [ ] Add `onboarding_completed` flag to `User` model + migration.
- [ ] Build Welcome screen (`/welcome`) — post magic-link landing, routes based on password/onboarding state.
- [ ] Build Set Password screen (`/set-password`).

### Phase 5: Onboarding Wizard (Revised to Match Flow Diagram)
- [ ] Revise `/onboarding` page to exact 5-step flow: About v0 → Project name → Project description → Brand voice → Social platforms.
- [ ] Persist onboarding completion state to backend (`onboarding_completed = true` on finish).
- [ ] Build Dashboard page (`/dashboard`) as post-onboarding destination.
  - Note: Dashboard is the main hub after first login; route guard: incomplete onboarding → redirect to welcome.

### Phase 6: Knowledge Manager + Vector DB + OpenRouter
- [ ] Add file upload endpoint (`POST /workflow/brand-assets/upload`) accepting `csv`, `txt`, `pdf`.
- [ ] Implement Knowledge Manager service: parse uploaded files, extract tone/keywords for brand profile.
- [ ] Add Vector DB support (MVP: pgvector extension on existing Postgres).
- [ ] Embed Context+Tone on brand profile save/update; store in vector table.
- [ ] Retrieve relevant context vectors in agent pipeline per generation request.
- [ ] Integrate OpenRouter as LLM router (replace/wrap current CrewAI/Agno/LangChain dispatch); prefer Claude for content.
- [ ] Add `GenerationHistory` DB model + migration (user_id, input, output, platform, created_at).
- [ ] Persist agent generation outputs to `GenerationHistory` on each content generation call.
- [ ] Add `GET /workflow/generation-history` endpoint for user history retrieval.

### Phase 7: Frontend Product Experience (Content Screens)
- [x] Build onboarding wizard (product -> brand -> assets) — partial, needs revision in Phase 5.
- [ ] Build weekly plan screen (`/plan`).
- [ ] Build generated posts review screen with edit controls (`/posts`).
- [ ] Build export screen — MVP JSON/CSV copy/export (`/export`).
- [x] Replace generic home messaging with product narrative from ideation docs.
  - 2026-03-11: Reworked homepage and site navigation for founder-content workflow and added `/waitlist` page.

### Phase 8: Launch Readiness (from Launch Strategy Doc)
- [ ] Add waitlist landing page v1 (hero, teaser area, email capture CTA).
- [ ] Add v2 sections support (social proof/testimonials placeholder, referral CTA placeholder).
- [ ] Add simple waitlist data capture endpoint/storage.
- [ ] Add basic analytics events (signup conversion, generate-plan conversion).

### Phase 9: QA and Documentation
- [ ] Add tests for onboarding, plan generation, and post generation APIs.
- [ ] Add tests for magic link auth flow.
- [ ] Add tests for file upload and knowledge manager parsing.
- [ ] Add frontend integration tests for core user flow.
- [ ] Update README and quickstart for new product workflow.
- [ ] Add API contract docs for frontend/backend alignment.

## Working Rules for This TODO
- Complete tasks in order unless a dependency requires reordering.
- After each completed task, update this file immediately:
  - change `[ ]` to `[x]`
  - add short note under the task if needed (date + commit reference)
- Do not start next phase until Phase 0 and Phase 1 are stable.

## Change Log
- 2026-03-11: Initial gap analysis and execution checklist created.
- 2026-03-11: Phase 0 completed and checklist updated with verification notes.
- 2026-03-11: Phase 4 partial frontend updates completed (home, nav, onboarding, waitlist, content studio copy).
- 2026-03-12: Phase 1 completed (domain models, schemas, migrations, and removal of generic items flow).
- 2026-03-12: Phase 2 completed with founder workflow APIs and Supabase integration status endpoint.
- 2026-03-12: Phase 3 completed with structured prompts, typed agent payloads, platform rules, and deterministic fixtures.
- 2026-03-12: Gap matrix and TODO updated from flow diagram (magic link auth, welcome/set-password screens, revised onboarding steps, dashboard) and architecture diagram (Knowledge Manager, Vector DB, OpenRouter, GenerationHistory). Old phases 4-6 renumbered to 7-9; new phases 4-6 inserted.
