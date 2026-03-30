"""
Ravah CLI — command-line interface for ravah.app
Directly uses backend database/service layer; no HTTP server required.

Usage:
    cd backend
    python cli.py --help
    python cli.py auth signup
    python cli.py workflow generate-posts --content-plan-id 1
"""

import json
import sys
from datetime import date as date_type, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

# Ensure the backend package is importable when running from the backend/ dir
sys.path.insert(0, str(Path(__file__).parent))

# ── App setup ─────────────────────────────────────────────────────────────────

app = typer.Typer(
    name="ravah",
    help="Ravah CLI — founder content workflow. Open-source at ravah.app",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
auth_app = typer.Typer(help="Authentication: signup, login, logout, me")
agent_app = typer.Typer(help="AI agent: query, status")
workflow_app = typer.Typer(help="Founder workflow: product ideas, brand profile, content plans, posts")

app.add_typer(auth_app, name="auth")
app.add_typer(agent_app, name="agent")
app.add_typer(workflow_app, name="workflow")

console = Console()

# Session stored at ~/.ravah/session.json
SESSION_PATH = Path.home() / ".ravah" / "session.json"


# ── Session helpers ───────────────────────────────────────────────────────────

def _load_session() -> dict:
    if SESSION_PATH.exists():
        try:
            return json.loads(SESSION_PATH.read_text())
        except Exception:
            return {}
    return {}


def _save_session(data: dict) -> None:
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps(data, indent=2))


def _require_token() -> str:
    session = _load_session()
    token = session.get("token")
    if not token:
        console.print("[red]Not logged in.[/red] Run: [bold]python cli.py auth login[/bold]")
        raise typer.Exit(1)
    return token


def _resolve_user(token: str, db):
    """Decode JWT and return the active User ORM object, or exit."""
    from app.utils.auth import verify_token
    from app.models import User

    username = verify_token(token)
    if not username:
        console.print("[red]Session expired.[/red] Run: [bold]python cli.py auth login[/bold]")
        raise typer.Exit(1)
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        console.print("[red]User not found or inactive.[/red]")
        raise typer.Exit(1)
    return user


def _get_db():
    from app.database import SessionLocal
    return SessionLocal()


# ── Health / serve ────────────────────────────────────────────────────────────

@app.command()
def health():
    """Check configuration and agent framework status."""
    from app.config import settings

    table = Table(title="Ravah — Health")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_row("Status", "[green]ok[/green]")
    table.add_row("App", f"{settings.APP_NAME} v{settings.APP_VERSION}")
    table.add_row("Agent framework", settings.AGENT_FRAMEWORK)
    table.add_row("Mock mode", str(settings.AGENT_MOCK_MODE))
    table.add_row("Database", settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL)
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
):
    """Start the FastAPI backend server (API + Swagger UI at /docs)."""
    import uvicorn

    console.print(f"[green]Starting Ravah API[/green] on http://{host}:{port}")
    console.print(f"  Swagger UI  → http://localhost:{port}/docs")
    console.print(f"  ReDoc       → http://localhost:{port}/redoc")
    uvicorn.run("main:app", host=host, port=port, reload=reload)


@app.command()
def integrations():
    """Show status of optional integrations (Supabase, Redis)."""
    from app.config import settings

    table = Table(title="Integrations")
    table.add_column("Integration", style="cyan")
    table.add_column("Status")
    table.add_column("Detail")

    supabase_ok = bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY)
    table.add_row(
        "Supabase",
        "[green]configured[/green]" if supabase_ok else "[yellow]not configured[/yellow]",
        settings.SUPABASE_URL or "Set SUPABASE_URL + SUPABASE_ANON_KEY in .env",
    )

    redis_ok = bool(settings.REDIS_URL)
    table.add_row(
        "Redis",
        "[green]configured[/green]" if redis_ok else "[yellow]not configured[/yellow]",
        settings.REDIS_URL or "Set REDIS_URL in .env (optional)",
    )

    table.add_row("OpenAI", "[green]key set[/green]" if settings.OPENAI_API_KEY != "mock-key" else "[yellow]mock key[/yellow]", settings.OPENAI_MODEL)
    console.print(table)


# ── Auth ──────────────────────────────────────────────────────────────────────

@auth_app.command("signup")
def auth_signup(
    email: str = typer.Option(..., prompt=True, help="Email address"),
    username: str = typer.Option(..., prompt=True, help="Username"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True, help="Password"),
):
    """Register a new account."""
    from app.database import SessionLocal
    from app.models import User
    from app.utils.auth import get_password_hash

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            console.print(f"[red]Email already registered:[/red] {email}")
            raise typer.Exit(1)
        if db.query(User).filter(User.username == username).first():
            console.print(f"[red]Username already taken:[/red] {username}")
            raise typer.Exit(1)

        user = User(email=email, username=username, hashed_password=get_password_hash(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        console.print(f"[green]Account created![/green] Welcome, {user.username} (ID: {user.id})")
        console.print("Next → [bold]python cli.py auth login[/bold]")
    finally:
        db.close()


@auth_app.command("login")
def auth_login(
    username: str = typer.Option(..., prompt=True, help="Username"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Password"),
):
    """Log in and save session token to ~/.ravah/session.json."""
    from app.config import settings
    from app.database import SessionLocal
    from app.models import User
    from app.utils.auth import create_access_token, verify_password

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        if not user or not verify_password(password, user.hashed_password):
            console.print("[red]Invalid username or password.[/red]")
            raise typer.Exit(1)

        token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        _save_session({"token": token, "username": user.username, "email": user.email})
        console.print(f"[green]Logged in as[/green] {user.username}")
        console.print(f"Session saved to {SESSION_PATH}")
    finally:
        db.close()


@auth_app.command("me")
def auth_me():
    """Show your profile."""
    token = _require_token()
    db = _get_db()
    try:
        user = _resolve_user(token, db)
        table = Table(title="Your Profile")
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        table.add_row("ID", str(user.id))
        table.add_row("Username", user.username)
        table.add_row("Email", user.email)
        table.add_row("Active", str(user.is_active))
        table.add_row("Created", str(user.created_at))
        console.print(table)
    finally:
        db.close()


@auth_app.command("logout")
def auth_logout():
    """Remove saved session token."""
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()
    console.print("[green]Logged out.[/green]")


# ── Agent ─────────────────────────────────────────────────────────────────────

@agent_app.command("query")
def agent_query(
    query: str = typer.Argument(..., help="Query string for the agent"),
    context: Optional[str] = typer.Option(None, help="Optional JSON context, e.g. '{\"platforms\":[\"linkedin\"]}'"),
    json_out: bool = typer.Option(False, "--json", help="Print raw JSON response"),
):
    """Send a query to the configured AI agent (mock or live)."""
    from app.factory import get_agent

    ctx: dict = {}
    if context:
        try:
            ctx = json.loads(context)
        except json.JSONDecodeError:
            console.print("[red]--context must be valid JSON.[/red]")
            raise typer.Exit(1)

    with console.status("[bold green]Querying agent…[/bold green]"):
        agent = get_agent()
        response = agent.process_query(query, ctx)

    if json_out:
        rprint(json.dumps(response.model_dump(), indent=2, default=str))
        return

    console.print(f"\n[bold cyan]Framework:[/bold cyan] {response.framework}")
    console.print(f"\n[bold]Result:[/bold]\n{response.result}")

    if response.structured:
        s = response.structured
        console.print(f"\n[bold cyan]Product:[/bold cyan] {s.product_name}")
        console.print(f"[bold cyan]Tone:[/bold cyan] {s.tone}")
        console.print(f"\n[bold cyan]Weekly themes ({len(s.weekly_themes)}):[/bold cyan]")
        for i, theme in enumerate(s.weekly_themes, 1):
            console.print(f"  {i}. {theme}")
        console.print(f"\n[bold cyan]Posts generated:[/bold cyan] {len(s.posts)}")


@agent_app.command("status")
def agent_status():
    """Show agent framework availability."""
    from app.config import settings
    from app.factory import get_agent

    try:
        agent = get_agent()
        available = agent.is_available()
        name = agent.get_framework_name()
    except Exception as exc:
        console.print(f"[red]Agent unavailable:[/red] {exc}")
        raise typer.Exit(1)

    table = Table(title="Agent Status")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Framework", name)
    table.add_row("Available", "[green]yes[/green]" if available else "[red]no[/red]")
    table.add_row("Mock mode", "[yellow]on[/yellow]" if settings.AGENT_MOCK_MODE else "[green]off (live)[/green]")
    table.add_row("OpenAI model", settings.OPENAI_MODEL)
    console.print(table)


# ── Workflow — Product Ideas ──────────────────────────────────────────────────

@workflow_app.command("create-product-idea")
def create_product_idea(
    product_name: str = typer.Option(..., prompt=True, help="Product name"),
    short_description: str = typer.Option(..., prompt=True, help="One-sentence description"),
    problem_statement: str = typer.Option(..., prompt=True, help="Problem it solves"),
    target_audience: str = typer.Option("", prompt="Target audience (optional, press Enter to skip)", help="Target audience"),
):
    """Create a new product idea (step 1 of the workflow)."""
    token = _require_token()
    from app.models import ProductIdea

    db = _get_db()
    try:
        user = _resolve_user(token, db)
        idea = ProductIdea(
            user_id=user.id,
            product_name=product_name,
            short_description=short_description,
            problem_statement=problem_statement,
            target_audience=target_audience or None,
        )
        db.add(idea)
        db.commit()
        db.refresh(idea)
        console.print(f"[green]Product idea created![/green] ID: {idea.id}")
        console.print(f"  Name        : {idea.product_name}")
        console.print(f"  Description : {idea.short_description}")
        console.print(f"\nNext → [bold]python cli.py workflow create-brand-profile[/bold]")
    finally:
        db.close()


@workflow_app.command("update-product-idea")
def update_product_idea(
    idea_id: int = typer.Argument(..., help="Product idea ID to update"),
    product_name: Optional[str] = typer.Option(None, help="New product name"),
    short_description: Optional[str] = typer.Option(None, help="New description"),
    problem_statement: Optional[str] = typer.Option(None, help="New problem statement"),
    target_audience: Optional[str] = typer.Option(None, help="New target audience"),
):
    """Update an existing product idea."""
    token = _require_token()
    from app.models import ProductIdea

    db = _get_db()
    try:
        user = _resolve_user(token, db)
        idea = db.query(ProductIdea).filter(
            ProductIdea.id == idea_id, ProductIdea.user_id == user.id
        ).first()
        if not idea:
            console.print(f"[red]Product idea {idea_id} not found.[/red]")
            raise typer.Exit(1)

        updates = {k: v for k, v in {
            "product_name": product_name,
            "short_description": short_description,
            "problem_statement": problem_statement,
            "target_audience": target_audience,
        }.items() if v is not None}

        if not updates:
            console.print("[yellow]No fields to update. Pass at least one option.[/yellow]")
            raise typer.Exit(0)

        for field, value in updates.items():
            setattr(idea, field, value)

        db.commit()
        db.refresh(idea)
        console.print(f"[green]Product idea {idea_id} updated.[/green]")
        console.print(f"  Name: {idea.product_name}")
    finally:
        db.close()


# ── Workflow — Brand Profile ──────────────────────────────────────────────────

@workflow_app.command("create-brand-profile")
def create_brand_profile(
    tone: str = typer.Option(..., prompt=True, help="Brand voice tone, e.g. 'clear and direct'"),
    keywords: str = typer.Option(..., prompt=True, help="Comma-separated brand keywords"),
    sample_post: str = typer.Option("", prompt="Sample post in your brand voice (optional)", help="Example post"),
    voice_guidelines: str = typer.Option("", prompt="Voice guidelines (optional)", help="Additional guidelines"),
):
    """Create your brand profile (step 2 of the workflow)."""
    token = _require_token()
    from app.models import BrandProfile

    db = _get_db()
    try:
        user = _resolve_user(token, db)
        existing = db.query(BrandProfile).filter(BrandProfile.user_id == user.id).first()
        if existing:
            console.print(f"[yellow]Brand profile already exists (ID: {existing.id}).[/yellow]")
            console.print("Use [bold]python cli.py workflow update-brand-profile[/bold] to update it.")
            raise typer.Exit(1)

        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
        profile = BrandProfile(
            user_id=user.id,
            tone=tone,
            keywords=kw_list,
            sample_post=sample_post or None,
            voice_guidelines=voice_guidelines or None,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        console.print(f"[green]Brand profile created![/green] ID: {profile.id}")
        console.print(f"  Tone     : {profile.tone}")
        console.print(f"  Keywords : {', '.join(profile.keywords or [])}")
        console.print(f"\nNext → [bold]python cli.py workflow generate-content-plan --product-idea-id <ID>[/bold]")
    finally:
        db.close()


@workflow_app.command("update-brand-profile")
def update_brand_profile(
    tone: Optional[str] = typer.Option(None, help="New tone"),
    keywords: Optional[str] = typer.Option(None, help="New comma-separated keywords"),
    sample_post: Optional[str] = typer.Option(None, help="New sample post"),
    voice_guidelines: Optional[str] = typer.Option(None, help="New voice guidelines"),
):
    """Update your brand profile."""
    token = _require_token()
    from app.models import BrandProfile

    db = _get_db()
    try:
        user = _resolve_user(token, db)
        profile = db.query(BrandProfile).filter(BrandProfile.user_id == user.id).first()
        if not profile:
            console.print("[red]No brand profile found.[/red] Run: [bold]python cli.py workflow create-brand-profile[/bold]")
            raise typer.Exit(1)

        if tone:
            profile.tone = tone
        if keywords:
            profile.keywords = [k.strip() for k in keywords.split(",") if k.strip()]
        if sample_post:
            profile.sample_post = sample_post
        if voice_guidelines:
            profile.voice_guidelines = voice_guidelines

        db.commit()
        db.refresh(profile)
        console.print(f"[green]Brand profile {profile.id} updated.[/green]")
    finally:
        db.close()


# ── Workflow — Brand Assets ───────────────────────────────────────────────────

@workflow_app.command("add-brand-asset")
def add_brand_asset(
    source_type: str = typer.Option("manual", help="Source type: figma | manual | upload"),
    figma_file_url: Optional[str] = typer.Option(None, help="Figma file URL"),
    logo_url: Optional[str] = typer.Option(None, help="Logo URL"),
    primary_color: Optional[str] = typer.Option(None, help="Primary hex color, e.g. #FF6B35"),
    secondary_color: Optional[str] = typer.Option(None, help="Secondary hex color"),
    typography: Optional[str] = typer.Option(None, help="Typography description"),
    brand_profile_id: Optional[int] = typer.Option(None, help="Brand profile ID to link (optional)"),
):
    """Ingest brand asset metadata (logo, colors, typography)."""
    token = _require_token()
    from app.models import BrandAsset, BrandProfile

    db = _get_db()
    try:
        user = _resolve_user(token, db)

        if brand_profile_id:
            profile = db.query(BrandProfile).filter(
                BrandProfile.id == brand_profile_id, BrandProfile.user_id == user.id
            ).first()
            if not profile:
                console.print(f"[red]Brand profile {brand_profile_id} not found.[/red]")
                raise typer.Exit(1)

        asset = BrandAsset(
            user_id=user.id,
            brand_profile_id=brand_profile_id,
            source_type=source_type,
            figma_file_url=figma_file_url,
            logo_url=logo_url,
            primary_color=primary_color,
            secondary_color=secondary_color,
            typography=typography,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        console.print(f"[green]Brand asset added![/green] ID: {asset.id}")
        console.print(f"  Source type : {asset.source_type}")
        if asset.primary_color:
            console.print(f"  Primary     : {asset.primary_color}")
    finally:
        db.close()


# ── Workflow — Content Plan ───────────────────────────────────────────────────

@workflow_app.command("generate-content-plan")
def generate_content_plan(
    product_idea_id: int = typer.Option(..., prompt=True, help="Product idea ID"),
    platforms: str = typer.Option("linkedin,x,instagram", help="Comma-separated platforms"),
    brand_profile_id: Optional[int] = typer.Option(None, help="Brand profile ID (optional)"),
    week_start: Optional[str] = typer.Option(None, help="Week start date YYYY-MM-DD (defaults to today)"),
):
    """Generate a 7-day content plan (step 3 of the workflow)."""
    token = _require_token()
    from app.models import BrandProfile, ContentPlan, ProductIdea
    from app.routers.workflow import _build_weekly_themes

    db = _get_db()
    try:
        user = _resolve_user(token, db)

        idea = db.query(ProductIdea).filter(
            ProductIdea.id == product_idea_id, ProductIdea.user_id == user.id
        ).first()
        if not idea:
            console.print(f"[red]Product idea {product_idea_id} not found.[/red]")
            raise typer.Exit(1)

        if brand_profile_id:
            profile = db.query(BrandProfile).filter(
                BrandProfile.id == brand_profile_id, BrandProfile.user_id == user.id
            ).first()
            if not profile:
                console.print(f"[red]Brand profile {brand_profile_id} not found.[/red]")
                raise typer.Exit(1)

        ws = date_type.fromisoformat(week_start) if week_start else date_type.today()
        platform_list = [p.strip() for p in platforms.split(",") if p.strip()]
        themes = _build_weekly_themes(idea.product_name, idea.short_description, idea.target_audience)

        plan = ContentPlan(
            user_id=user.id,
            product_idea_id=idea.id,
            brand_profile_id=brand_profile_id,
            week_start=ws,
            platforms=platform_list,
            weekly_themes=themes,
            plan_notes="Auto-generated baseline plan. Customize before publishing.",
            status="draft",
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        console.print(f"[green]Content plan generated![/green] ID: {plan.id}")
        console.print(f"  Product   : {idea.product_name}")
        console.print(f"  Week start: {plan.week_start}")
        console.print(f"  Platforms : {', '.join(platform_list)}")

        table = Table(title="Weekly Themes")
        table.add_column("Day", style="cyan", width=4)
        table.add_column("Theme")
        for i, theme in enumerate(themes, 1):
            table.add_row(str(i), theme)
        console.print(table)

        console.print(f"\nNext → [bold]python cli.py workflow generate-posts --content-plan-id {plan.id}[/bold]")
    finally:
        db.close()


# ── Workflow — Content Posts ──────────────────────────────────────────────────

@workflow_app.command("generate-posts")
def generate_posts(
    content_plan_id: int = typer.Option(..., prompt=True, help="Content plan ID"),
    replace_existing: bool = typer.Option(False, "--replace", help="Delete and regenerate existing posts"),
    json_out: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Generate platform-specific posts from a content plan (step 4 of the workflow)."""
    token = _require_token()
    from app.models import BrandProfile, ContentPlan, ContentPost
    from app.routers.workflow import _caption_for_platform, _hashtags_for_platform

    db = _get_db()
    try:
        user = _resolve_user(token, db)

        plan = db.query(ContentPlan).filter(
            ContentPlan.id == content_plan_id, ContentPlan.user_id == user.id
        ).first()
        if not plan:
            console.print(f"[red]Content plan {content_plan_id} not found.[/red]")
            raise typer.Exit(1)

        if replace_existing:
            db.query(ContentPost).filter(ContentPost.content_plan_id == plan.id).delete()
            db.commit()

        profile = None
        if plan.brand_profile_id:
            profile = db.query(BrandProfile).filter(
                BrandProfile.id == plan.brand_profile_id, BrandProfile.user_id == user.id
            ).first()

        themes = plan.weekly_themes or []
        platforms = plan.platforms or ["linkedin", "x", "instagram"]

        with console.status("[bold green]Generating posts…[/bold green]"):
            for day_index, theme in enumerate(themes, start=1):
                for order, platform in enumerate(platforms, start=1):
                    hook, caption = _caption_for_platform(platform, theme, profile.tone if profile else None)
                    post = ContentPost(
                        user_id=user.id,
                        content_plan_id=plan.id,
                        platform=platform,
                        day_index=day_index,
                        post_order=order,
                        hook=hook,
                        caption=caption,
                        hashtags=_hashtags_for_platform(platform),
                        visual_prompt=f"{theme} in a clean founder-story visual style for {platform}.",
                        status="draft",
                    )
                    db.add(post)

            plan.status = "generated"
            db.commit()

        posts = (
            db.query(ContentPost)
            .filter(ContentPost.content_plan_id == plan.id)
            .order_by(ContentPost.day_index.asc(), ContentPost.post_order.asc())
            .all()
        )

        if json_out:
            output = [
                {
                    "id": p.id,
                    "platform": p.platform,
                    "day_index": p.day_index,
                    "hook": p.hook,
                    "caption": p.caption,
                    "hashtags": p.hashtags,
                    "visual_prompt": p.visual_prompt,
                    "status": p.status,
                }
                for p in posts
            ]
            rprint(json.dumps(output, indent=2, default=str))
            return

        console.print(f"[green]Generated {len(posts)} posts![/green]\n")
        table = Table(title=f"Plan {content_plan_id} — Posts")
        table.add_column("Day", style="cyan", width=4)
        table.add_column("Platform", style="magenta", width=12)
        table.add_column("Hook")
        table.add_column("Status", width=10)
        for post in posts:
            hook_display = post.hook[:60] + "…" if len(post.hook) > 60 else post.hook
            table.add_row(str(post.day_index), post.platform, hook_display, post.status)
        console.print(table)
    finally:
        db.close()


# ── Generate — full onboarding → Gemini → MD output ──────────────────────────

_STYLE_CHOICES = {
    "1": ("educational", "Educational — teach something actionable"),
    "2": ("storytelling", "Storytelling — narrative with a beginning, middle, and lesson"),
    "3": ("motivational", "Motivational — inspire action or mindset shift"),
    "4": ("behind_the_scenes", "Behind the Scenes — raw, authentic, unfiltered"),
    "5": ("mixed", "Mixed — rotate through styles across the days"),
}

_TONE_PRESETS = {
    "1": "Casual & friendly",
    "2": "Professional & authoritative",
    "3": "Conversational & approachable",
    "4": "Bold & direct",
    "5": "Witty & playful",
}

_PLATFORM_LABELS = {"x": "X (Twitter)", "instagram": "Instagram", "linkedin": "LinkedIn"}


def _prompt_choice(console: Console, question: str, choices: dict[str, tuple[str, str] | str]) -> str:
    """Render a numbered menu and return the value for the chosen key."""
    console.print(f"\n[bold cyan]{question}[/bold cyan]")
    for key, val in choices.items():
        label = val[1] if isinstance(val, tuple) else val
        console.print(f"  [{key}] {label}")
    while True:
        raw = typer.prompt("Your choice").strip()
        if raw in choices:
            return raw
        console.print(f"[red]Please enter one of: {', '.join(choices.keys())}[/red]")


def _render_clearv_panel(console: Console, post) -> None:
    """Print a single post's ClearV breakdown + full post to the terminal."""
    from rich.panel import Panel
    from rich.text import Text

    pname = _PLATFORM_LABELS.get(post.platform, post.platform)
    cv = post.clearv

    body = Text()
    body.append("C – Capture:  ", style="bold yellow")
    body.append(cv.capture + "\n")
    body.append("L – Lead:     ", style="bold green")
    body.append(cv.lead + "\n")
    body.append("E – Educate:  ", style="bold blue")
    body.append(cv.educate + "\n")
    body.append("A – Activate: ", style="bold magenta")
    body.append(cv.activate + "\n")
    body.append("R – Resonate: ", style="bold red")
    body.append(cv.resonate + "\n")
    body.append("V – Visual:   ", style="bold white")
    body.append(cv.visual + "\n\n")
    body.append("── Full post ──\n", style="dim")
    body.append(post.full_post + "\n\n")
    body.append(f"Hashtags: {' '.join(post.hashtags)}  •  {post.char_count} chars", style="dim")

    console.print(Panel(body, title=f"[bold]Day {post.day} — {pname}[/bold]", border_style="cyan"))


@app.command()
def generate():
    """
    Interactive post generator — onboarding questions → Google Gemini → ClearV posts → Markdown file.

    Covers building-in-public and product content modes.
    Generates posts for X, Instagram, and LinkedIn using the ClearV framework.
    """
    from app.config import settings

    console.rule("[bold cyan]Ravah — Content Generator[/bold cyan]")
    console.print("[dim]Powered by Google Gemini · ClearV Framework · ravah.app[/dim]\n")

    # ── 1. Check API key ──────────────────────────────────────────────────────
    api_key = settings.GOOGLE_API_KEY
    if not api_key or api_key == "your-google-ai-api-key-here":
        console.print(
            "[red]GOOGLE_API_KEY is not set.[/red]\n"
            "Add it to your [bold].env[/bold] file:\n\n"
            "  GOOGLE_API_KEY=your-key-here\n\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )
        raise typer.Exit(1)

    # ── 2. Mode ───────────────────────────────────────────────────────────────
    mode_key = _prompt_choice(
        console,
        "What are you doing?",
        {
            "1": ("building_in_public", "Building in public  (sharing my founder/creator journey openly)"),
            "2": ("product_content",    "Posting about my product/service/content"),
        },
    )
    mode = ("building_in_public", "product_content")[int(mode_key) - 1]

    # ── 3. Summary ────────────────────────────────────────────────────────────
    console.print("\n[bold cyan]Give me a summary of what you're building or trying to achieve.[/bold cyan]")
    console.print("[dim]Be specific — the more detail, the better your posts.[/dim]")
    summary = typer.prompt("Summary").strip()
    while len(summary) < 20:
        console.print("[red]Please write at least a few sentences so Gemini has enough context.[/red]")
        summary = typer.prompt("Summary").strip()

    # ── 4. Duration ───────────────────────────────────────────────────────────
    days_key = _prompt_choice(
        console,
        "How many days of content do you want?",
        {"1": "7 days", "2": "18 days", "3": "30 days"},
    )
    num_days = {"1": 7, "2": 18, "3": 30}[days_key]

    # ── 5. Platforms ──────────────────────────────────────────────────────────
    console.print("\n[bold cyan]Which platforms?[/bold cyan]")
    console.print("  Press [bold]Enter[/bold] to use all three, or type a comma-separated subset.")
    console.print("  Options: [bold]x[/bold], [bold]instagram[/bold], [bold]linkedin[/bold]")
    raw_platforms = typer.prompt("Platforms", default="x,instagram,linkedin").strip().lower()
    platforms = [p.strip() for p in raw_platforms.split(",") if p.strip() in ("x", "instagram", "linkedin")]
    if not platforms:
        platforms = ["x", "instagram", "linkedin"]
    console.print(f"  Selected: {', '.join(_PLATFORM_LABELS[p] for p in platforms)}")

    # ── 6. Style ──────────────────────────────────────────────────────────────
    style_key = _prompt_choice(console, "What content style fits you best?", _STYLE_CHOICES)
    style = _STYLE_CHOICES[style_key][0]

    # ── 7. Tone ───────────────────────────────────────────────────────────────
    tone_key = _prompt_choice(
        console,
        "What tone should your posts have?",
        {**_TONE_PRESETS, "6": "Custom — I'll type my own"},
    )
    if tone_key == "6":
        tone = typer.prompt("Describe your tone").strip()
    else:
        tone = _TONE_PRESETS[tone_key]

    # ── 8. Audience ───────────────────────────────────────────────────────────
    console.print("\n[bold cyan]Who is your target audience?[/bold cyan]")
    console.print("[dim]e.g. 'early-stage SaaS founders', 'fitness coaches', 'indie hackers'[/dim]")
    audience = typer.prompt("Audience").strip() or "early adopters and founders"

    # ── 9. Keywords / topics ──────────────────────────────────────────────────
    console.print("\n[bold cyan]Any keywords, hashtags, or recurring topics to always include?[/bold cyan]")
    console.print("[dim]Optional — press Enter to skip[/dim]")
    keywords = typer.prompt("Keywords", default="").strip()

    # ── 10. Avoid ─────────────────────────────────────────────────────────────
    console.print("\n[bold cyan]Anything you want Gemini to avoid in the posts?[/bold cyan]")
    console.print("[dim]Optional — e.g. 'no emojis', 'don't mention competitors'[/dim]")
    avoid = typer.prompt("Avoid", default="").strip()

    # ── Confirm ───────────────────────────────────────────────────────────────
    console.print()
    console.rule("[bold green]Your settings[/bold green]")
    summary_table = Table(show_header=False, box=None, padding=(0, 1))
    summary_table.add_column("Field", style="cyan")
    summary_table.add_column("Value")
    summary_table.add_row("Mode", mode.replace("_", " ").title())
    summary_table.add_row("Days", str(num_days))
    summary_table.add_row("Platforms", ", ".join(_PLATFORM_LABELS[p] for p in platforms))
    summary_table.add_row("Style", _STYLE_CHOICES[style_key][1].split(" — ")[0])
    summary_table.add_row("Tone", tone)
    summary_table.add_row("Audience", audience)
    if keywords:
        summary_table.add_row("Keywords", keywords)
    if avoid:
        summary_table.add_row("Avoid", avoid)
    console.print(summary_table)
    console.print()

    total_posts = num_days * len(platforms)
    confirmed = typer.confirm(
        f"Generate {total_posts} posts ({num_days} days × {len(platforms)} platforms)?",
        default=True,
    )
    if not confirmed:
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(0)

    # ── Call Gemini ───────────────────────────────────────────────────────────
    from app.gemini_service import GenerationContext, generate_posts, render_markdown

    ctx = GenerationContext(
        mode=mode,
        summary=summary,
        num_days=num_days,
        platforms=platforms,
        style=style,
        tone=tone,
        audience=audience,
        keywords=keywords,
        avoid=avoid,
    )

    console.print()
    with console.status(
        f"[bold green]Asking Gemini ({settings.GOOGLE_AI_MODEL}) to write {total_posts} posts…[/bold green]",
        spinner="dots",
    ):
        try:
            posts = generate_posts(ctx, api_key=api_key, model=settings.GOOGLE_AI_MODEL)
        except Exception as exc:
            console.print(f"\n[red]Generation failed:[/red] {exc}")
            raise typer.Exit(1)

    console.print(f"[green]Got {len(posts)} posts from Gemini.[/green]\n")

    # ── Save MD file ──────────────────────────────────────────────────────────
    from datetime import datetime

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = output_dir / f"posts_{timestamp}_{num_days}d.md"
    md_content = render_markdown(posts, ctx)
    md_path.write_text(md_content, encoding="utf-8")

    # ── Display in CLI ────────────────────────────────────────────────────────
    console.rule("[bold cyan]Your Posts[/bold cyan]")

    # Group by day
    days: dict[int, list] = {}
    for post in posts:
        days.setdefault(post.day, []).append(post)

    for day_num in sorted(days.keys()):
        console.print(f"\n[bold white on blue]  Day {day_num}  [/bold white on blue]\n")
        for post in days[day_num]:
            _render_clearv_panel(console, post)

    # ── Summary footer ────────────────────────────────────────────────────────
    console.rule()
    console.print(f"\n[green]Done![/green] {len(posts)} posts generated.")
    console.print(f"Markdown saved to: [bold]{md_path}[/bold]")
    console.print(
        "\n[dim]Tip: open the .md file to copy individual posts, "
        "or run again with different settings to iterate.[/dim]"
    )


if __name__ == "__main__":
    app()
