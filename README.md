# Ravah

![Ravah](broken_ravah.png)

**Turn what you ship into a week of social content.**
For founders who build in public.

Open-source CLI

---

## Install

```bash
pip install git+https://github.com/muhtalhakhan/Ravah-App-OpenSource.git
```

That's it. No database, no config files, no `cd` into anything.

---

## Run

```bash
ravah
```

**First run** — asked once, saved forever:

```text
Paste your Google AI API key  →  saved to ~/.ravah/profile.json
What's your name?             →  saved
Creating content for:
  [1] Myself — personal brand
  [2] A brand or product
  [3] Building in public    →  saved

What are you building or shipping?
How many days?  →  7 / 18 / 30
Platforms?      →  x, instagram, linkedin
Style?          →  Educational / Storytelling / Motivational / Behind the scenes / Mixed
Tone?           →  5 presets or custom
Audience?       →  ...
Keywords?       →  (optional)
Avoid?          →  (optional)

→ Gemini writes your posts
→ Printed to terminal
→ Saved to output/posts_<timestamp>.md
→ Context saved to ~/.ravah/last_session.json
```

**Every run after** — picks up where you left off:

```text
Welcome back, Muhammad · Building in public

Last session (2026-03-30): Building a CLI tool that turns weekly...

  [1] Start fresh — I'm working on something new
  [2] Carry on — keep going with the old content

→ [1] asks all content questions fresh
→ [2] loads saved context, only asks how many days
```

Get a free API key at [aistudio.google.com](https://aistudio.google.com/app/apikey).

---

## ClearV framework

Every post is structured as six components:

| | What it does |
| - | ------------ |
| **C** Capture | Scroll-stopping first line |
| **L** Lead | The single core message |
| **E** Educate | Insight, story, or data that backs it up |
| **A** Activate | Call-to-action |
| **R** Resonate | Emotionally sticky closing line |
| **V** Visual | Ideal image or graphic description |

---

## Other commands

```bash
ravah health    # show model, API key, profile, and last session info
ravah reset     # clear saved profile and last session — start completely fresh
```

---

## Customise it

Two files to edit:

**[ravah/cli.py](https://github.com/muhtalhakhan/Ravah-App-OpenSource/blob/main/ravah/cli.py)** — every command is a plain `@app.command()` function. Add yours the same way. The onboarding questions are all inside `generate()`.

**[ravah/gemini_service.py](https://github.com/muhtalhakhan/Ravah-App-OpenSource/blob/main/ravah/gemini_service.py)** — the system prompt, ClearV definition, and platform specs.

| What to change | Where |
| -------------- | ----- |
| Content framework (swap ClearV for AIDA, PAS, etc.) | `_build_system_prompt()` and `_build_user_prompt()` in `gemini_service.py` |
| AI model | `GOOGLE_AI_MODEL` in `.env` |
| Add a platform (TikTok, Threads) | `_PLATFORM_SPECS` in `gemini_service.py` + `_PLATFORM_LABELS` in `cli.py` |
| Duration options | `days_key` dict inside `generate()` in `cli.py` |
| New command | Add `@app.command()` function to `cli.py` |

---

## Configuration

Only `GOOGLE_API_KEY` is needed to generate posts. Everything else is optional.

```env
GOOGLE_API_KEY=your-key-here
GOOGLE_AI_MODEL=gemini-2.5-flash-preview-04-17
```

The API key can also be entered on first run — it will be saved locally and `.env` becomes optional.

---

## Contributing

Clone and run from source with editable install — changes reflect immediately:

```bash
git clone https://github.com/muhtalhakhan/Ravah-App-OpenSouce.git
cd Ravah-App-OpenSource
pip install -e .
ravah
```

---

## Frontend (optional)

An Astro 4 + Tailwind UI is included. The CLI works without it.

```bash
cd frontend && pnpm install && pnpm dev    # http://localhost:4321
```

---

Issues and PRs welcome.
