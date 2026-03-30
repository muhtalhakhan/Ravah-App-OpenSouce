"""
Founder workflow routes for onboarding and content generation.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BrandAsset, BrandProfile, ContentPlan, ContentPost, ProductIdea, User
from app.schemas import (
    BrandAssetCreate,
    BrandAssetResponse,
    BrandProfileCreate,
    BrandProfileResponse,
    BrandProfileUpdate,
    ContentPlanResponse,
    ContentPostResponse,
    GenerateContentPlanRequest,
    GenerateContentPostsRequest,
    GenerateContentPostsResponse,
    ProductIdeaCreate,
    ProductIdeaResponse,
    ProductIdeaUpdate,
)
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/workflow", tags=["Founder Workflow"])


@router.post("/product-ideas", response_model=ProductIdeaResponse, status_code=status.HTTP_201_CREATED)
def create_product_idea(
    payload: ProductIdeaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    idea = ProductIdea(user_id=current_user.id, **payload.model_dump())
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


@router.put("/product-ideas/{idea_id}", response_model=ProductIdeaResponse)
def update_product_idea(
    idea_id: int,
    payload: ProductIdeaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    idea = db.query(ProductIdea).filter(ProductIdea.id == idea_id, ProductIdea.user_id == current_user.id).first()
    if not idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product idea not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(idea, field, value)

    db.commit()
    db.refresh(idea)
    return idea


@router.post("/brand-profile", response_model=BrandProfileResponse, status_code=status.HTTP_201_CREATED)
def create_brand_profile(
    payload: BrandProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand profile already exists. Use PUT /workflow/brand-profile to update.",
        )

    profile = BrandProfile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/brand-profile", response_model=BrandProfileResponse)
def update_brand_profile(
    payload: BrandProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/brand-assets/ingest", response_model=BrandAssetResponse, status_code=status.HTTP_201_CREATED)
def ingest_brand_asset_metadata(
    payload: BrandAssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if payload.brand_profile_id is not None:
        profile = (
            db.query(BrandProfile)
            .filter(BrandProfile.id == payload.brand_profile_id, BrandProfile.user_id == current_user.id)
            .first()
        )
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand profile not found")

    asset = BrandAsset(user_id=current_user.id, **payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def _build_weekly_themes(product_name: str, short_description: str, target_audience: str | None) -> list[str]:
    audience = target_audience or "early adopters"
    theme_templates = [
        "Problem framing for {audience}",
        "Product insight: {description}",
        "Behind the scenes building {product}",
        "Founder lesson learned this week",
        "Customer use case spotlight",
        "Myth vs reality in this space",
        "Weekly recap and next milestone",
    ]
    return [
        f"{product_name}: {template.format(audience=audience, description=short_description, product=product_name)}"
        for template in theme_templates
    ]


@router.post("/content-plans/generate", response_model=ContentPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_weekly_content_plan(
    payload: GenerateContentPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    product_idea = (
        db.query(ProductIdea)
        .filter(ProductIdea.id == payload.product_idea_id, ProductIdea.user_id == current_user.id)
        .first()
    )
    if not product_idea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product idea not found")

    if payload.brand_profile_id is not None:
        profile = (
            db.query(BrandProfile)
            .filter(BrandProfile.id == payload.brand_profile_id, BrandProfile.user_id == current_user.id)
            .first()
        )
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand profile not found")

    week_start = payload.week_start or date.today()
    themes = _build_weekly_themes(
        product_name=product_idea.product_name,
        short_description=product_idea.short_description,
        target_audience=product_idea.target_audience,
    )

    plan = ContentPlan(
        user_id=current_user.id,
        product_idea_id=product_idea.id,
        brand_profile_id=payload.brand_profile_id,
        week_start=week_start,
        platforms=payload.platforms,
        weekly_themes=themes,
        plan_notes="Auto-generated baseline plan. Customize before publishing.",
        status="draft",
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def _hashtags_for_platform(platform: str) -> list[str]:
    base_tags = ["#buildinpublic", "#founder", "#startups"]
    if platform == "linkedin":
        return base_tags + ["#leadership", "#growth"]
    if platform == "x":
        return base_tags + ["#shipit", "#indiehacker"]
    if platform == "instagram":
        return base_tags + ["#brandstory", "#creator"]
    return base_tags


def _caption_for_platform(platform: str, theme: str, tone: str | None) -> tuple[str, str]:
    chosen_tone = tone or "clear and actionable"
    if platform == "x":
        hook = f"{theme[:95]}..."
        caption = f"{theme}. Built for founders. Tone: {chosen_tone}. What would you test next?"
    elif platform == "instagram":
        hook = f"Swipe into: {theme}"
        caption = f"{theme}\n\nFounder playbook in one post. Voice: {chosen_tone}."
    else:
        hook = f"Founder insight: {theme}"
        caption = f"{theme}. Here is what this means for operators this week. Voice: {chosen_tone}."
    return hook, caption


@router.post(
    "/content-posts/generate",
    response_model=GenerateContentPostsResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_platform_posts(
    payload: GenerateContentPostsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    plan = (
        db.query(ContentPlan)
        .filter(ContentPlan.id == payload.content_plan_id, ContentPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content plan not found")

    if payload.replace_existing:
        db.query(ContentPost).filter(ContentPost.content_plan_id == plan.id).delete()
        db.commit()

    profile = None
    if plan.brand_profile_id:
        profile = (
            db.query(BrandProfile)
            .filter(BrandProfile.id == plan.brand_profile_id, BrandProfile.user_id == current_user.id)
            .first()
        )

    themes = plan.weekly_themes or []
    platforms = plan.platforms or ["linkedin", "x", "instagram"]

    new_posts: list[ContentPost] = []
    for day_index, theme in enumerate(themes, start=1):
        for order, platform in enumerate(platforms, start=1):
            hook, caption = _caption_for_platform(platform, theme, profile.tone if profile else None)
            post = ContentPost(
                user_id=current_user.id,
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
            new_posts.append(post)

    db.commit()

    posts = db.query(ContentPost).filter(ContentPost.content_plan_id == plan.id).order_by(
        ContentPost.day_index.asc(), ContentPost.post_order.asc()
    ).all()

    plan.status = "generated"
    db.commit()
    db.refresh(plan)

    return GenerateContentPostsResponse(content_plan=plan, posts=posts)
