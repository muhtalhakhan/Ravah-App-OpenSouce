"""
Basic tests for the FastAPI application.
"""

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Use SQLite during tests to avoid requiring a running local PostgreSQL instance.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["AGENT_MOCK_MODE"] = "True"

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "agent_framework" in data


def test_openapi_docs():
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_signup_endpoint():
    """Test user signup endpoint."""
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
        },
    )
    # May fail if user already exists, but endpoint should be reachable
    assert response.status_code in [201, 400]


def test_login_endpoint_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_items_endpoint_removed():
    """Test that deprecated items endpoint is no longer available."""
    response = client.get("/items")
    assert response.status_code == 404


def test_agent_status_endpoint():
    """Test agent status endpoint (no auth required)."""
    response = client.get("/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert "framework" in data
    assert "available" in data
    assert "mock_mode" in data


def test_agent_query_structured_output_and_platform_constraints():
    """Agent query should return structured payload with platform constraints applied."""
    response = client.post(
        "/agent/query",
        json={
            "query": "Generate a weekly launch plan",
            "context": {
                "product_name": "Rawah",
                "short_description": "AI content studio for founders",
                "tone": "confident and practical",
                "keywords": ["founder", "launch", "story"],
                "platforms": ["linkedin", "x", "instagram"],
            },
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["structured"] is not None
    assert len(data["structured"]["weekly_themes"]) == 7
    assert len(data["structured"]["posts"]) == 21

    for post in data["structured"]["posts"]:
        rule = post["rule_applied"]
        assert post["caption_chars"] <= rule["max_caption_chars"]
        assert post["hook_chars"] <= rule["max_hook_chars"]


def test_auth_and_agent_status_smoke():
    """Smoke test for auth and agent status flow."""
    suffix = uuid4().hex[:8]
    username = f"smokeuser_{suffix}"
    password = "smokepassword123"

    signup_response = client.post(
        "/auth/signup",
        json={
            "email": f"smoke_{suffix}@example.com",
            "username": username,
            "password": password,
        },
    )
    assert signup_response.status_code in [201, 400]

    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200

    agent_response = client.get("/agent/status")
    assert agent_response.status_code == 200


def test_workflow_phase2_endpoints_smoke():
    """Smoke test for phase 2 founder workflow APIs."""
    suffix = uuid4().hex[:8]
    username = f"workflowuser_{suffix}"
    password = "workflowpassword123"

    client.post(
        "/auth/signup",
        json={
            "email": f"workflow_{suffix}@example.com",
            "username": username,
            "password": password,
        },
    )

    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    idea_response = client.post(
        "/workflow/product-ideas",
        headers=headers,
        json={
            "product_name": "Rawah",
            "short_description": "AI founder content studio",
            "problem_statement": "Founders struggle with consistent content",
            "target_audience": "B2B SaaS founders",
        },
    )
    assert idea_response.status_code == 201
    product_idea_id = idea_response.json()["id"]

    brand_response = client.post(
        "/workflow/brand-profile",
        headers=headers,
        json={
            "tone": "confident and practical",
            "keywords": ["clarity", "execution"],
            "sample_post": "Shipping each week beats planning forever.",
            "voice_guidelines": "Write directly and avoid fluff.",
        },
    )
    assert brand_response.status_code == 201
    brand_profile_id = brand_response.json()["id"]

    asset_response = client.post(
        "/workflow/brand-assets/ingest",
        headers=headers,
        json={
            "brand_profile_id": brand_profile_id,
            "source_type": "figma",
            "figma_file_url": "https://www.figma.com/file/example",
            "primary_color": "#111111",
            "secondary_color": "#F7F7F7",
            "typography": "Sora",
            "metadata_json": {"logo": "wordmark"},
        },
    )
    assert asset_response.status_code == 201

    plan_response = client.post(
        "/workflow/content-plans/generate",
        headers=headers,
        json={
            "product_idea_id": product_idea_id,
            "brand_profile_id": brand_profile_id,
            "platforms": ["linkedin", "x", "instagram"],
        },
    )
    assert plan_response.status_code == 201
    plan_id = plan_response.json()["id"]

    posts_response = client.post(
        "/workflow/content-posts/generate",
        headers=headers,
        json={"content_plan_id": plan_id, "replace_existing": True},
    )
    assert posts_response.status_code == 201
    assert len(posts_response.json()["posts"]) > 0


def test_supabase_status_endpoint():
    """Integration status endpoint should always be reachable."""
    response = client.get("/integrations/supabase/status")
    assert response.status_code == 200
    payload = response.json()
    assert "configured" in payload
    assert "uses_supabase_db" in payload
