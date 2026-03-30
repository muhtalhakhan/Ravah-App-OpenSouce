"""
Integration utility routes.
"""

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("/supabase/status")
def supabase_status():
    """Return Supabase integration readiness for local/dev diagnostics."""
    database_url = settings.DATABASE_URL.lower()
    uses_supabase_db = "supabase" in database_url

    return {
        "configured": bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY),
        "uses_supabase_db": uses_supabase_db,
        "has_service_role": bool(settings.SUPABASE_SERVICE_ROLE_KEY),
        "auth_mode": settings.AUTH_PROVIDER,
    }
