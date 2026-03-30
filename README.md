# Ravah

![Ravah](broken_ravah.png)

Open-source founder content platform · [ravah.app](https://ravah.app)

---

## What is this?

Ravah is a CLI-first tool that takes a short description of what you are building and generates a full content calendar — posts for X, Instagram, and LinkedIn — using Google Gemini and the **ClearV framework**.

The frontend and REST API are included but optional. Everything works from the terminal.

---

## Quick start

```bash
git clone <repo-url>
cd Architecture-Rawah/backend

pip install -r requirements.txt
cp ../.env.example .env          # add DATABASE_URL, JWT_SECRET_KEY, GOOGLE_API_KEY

alembic upgrade head             # or use SQLite: DATABASE_URL=sqlite:///./dev.db
python cli.py health             # verify setup
```

> **No Postgres?** Set `DATABASE_URL=sqlite:///./dev.db` in `.env` and skip the Alembic step for the `generate` command — it has no database dependency.

---

## Generate posts

```bash
python cli.py generate
```

Walks you through 9 questions, calls Gemini, and writes every post to the terminal and to `backend/output/posts_<timestamp>.md`.

| # | Prompt | Choices |
| - | ------ | ------- |
| 1 | Mode | Building in public / Product content |
| 2 | Summary | Free text |
| 3 | Duration | 7 / 18 / 30 days |
| 4 | Platforms | x, instagram, linkedin |
| 5 | Style | Educational / Storytelling / Motivational / Behind the scenes / Mixed |
| 6 | Tone | 5 presets or custom |
| 7 | Audience | Free text |
| 8 | Keywords | Optional |
| 9 | Avoid | Optional |

**ClearV framework** — every post is structured as:

| | Component | Purpose |
| - | --------- | ------- |
| C | Capture | Scroll-stopping hook |
| L | Lead | Single core message |
| E | Educate | Insight, story, or data |
| A | Activate | Call-to-action |
| R | Resonate | Emotionally sticky close |
| V | Visual | Image/graphic description |

Requires `GOOGLE_API_KEY` in `.env`. Free key at [aistudio.google.com](https://aistudio.google.com/app/apikey).

---

## All CLI commands

```bash
python cli.py --help                            # list everything
python cli.py generate                          # AI post generator
python cli.py health                            # config + status check
python cli.py serve                             # start API server (localhost:8000)
python cli.py integrations                      # Supabase / Redis / OpenAI status

python cli.py auth signup / login / me / logout
python cli.py agent query "<text>"
python cli.py agent status

python cli.py workflow create-product-idea
python cli.py workflow create-brand-profile
python cli.py workflow generate-content-plan --product-idea-id 1
python cli.py workflow generate-posts --content-plan-id 1
```

---

## Customise it for your use case

The CLI is two files. Edit them freely.

**[backend/cli.py](backend/cli.py)** — every command is a plain `@app.command()` function. Add yours the same way.

**[backend/app/gemini_service.py](backend/app/gemini_service.py)** — holds the system prompt, ClearV definition, and platform specs. Common changes:

- **Swap the content framework** — edit `_build_system_prompt()` and the ClearV block in `_build_user_prompt()`. Replace with AIDA, PAS, StoryBrand, or anything else.
- **Change the model** — set `GOOGLE_AI_MODEL` in `.env` (`gemini-2.5-flash-preview-04-17` by default).
- **Add a platform** — add an entry to `_PLATFORM_SPECS`, then add it to the platform prompt in `generate()`.
- **Change duration options** — edit the `days_key` dict in `generate()`.

---

## Configuration

```env
# Required
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agentapp
JWT_SECRET_KEY=<openssl rand -hex 32>

# Google AI — for `python cli.py generate`
GOOGLE_API_KEY=your-key-here
GOOGLE_AI_MODEL=gemini-2.5-flash-preview-04-17

# Agent (mock works without API keys)
AGENT_FRAMEWORK=crewai
AGENT_MOCK_MODE=True
OPENAI_API_KEY=sk-...            # only needed when AGENT_MOCK_MODE=False

# Optional
REDIS_URL=redis://localhost:6379/0
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=...
```

---

## API (optional)

Start the server with `python cli.py serve` and open `http://localhost:8000/docs`.

Key endpoints: `POST /auth/signup` · `POST /auth/login` · `POST /agent/query` · `POST /workflow/content-plans/generate` · `POST /workflow/content-posts/generate`

---

## Frontend (optional)

An Astro 4 + Tailwind web UI is included but not required. To run it:

```bash
cd frontend
pnpm install
pnpm dev        # http://localhost:4321
```

---

## Project structure

```text
backend/
├── app/
│   ├── gemini_service.py   ← prompt + ClearV logic
│   ├── models/             ← SQLAlchemy models
│   ├── routers/            ← FastAPI routes
│   ├── schemas/            ← Pydantic schemas
│   └── config.py           ← settings from .env
├── cli.py                  ← all CLI commands
├── main.py                 ← FastAPI entry point
└── output/                 ← generated Markdown files
frontend/                   ← Astro UI (optional)
```

---

## Contributing

Open an issue before large changes. PRs welcome.

**[ravah.app](https://ravah.app)**
