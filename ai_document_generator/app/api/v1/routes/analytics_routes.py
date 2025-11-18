"""
Analytics routes following functional patterns and RORO
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_superuser
from app.core.errors import handle_validation_error, handle_internal_error
from app.schemas.user import User
from app.services.analytics_service import (
    get_document_analytics, get_user_analytics, get_organization_analytics,
    get_system_analytics, get_ai_usage_analytics
)
from app.utils.validators import validate_date_range
from app.utils.rate_limiter import rate_limit_search

router = APIRouter()


async def get_document_analytics_endpoint(
    document_id: str,
    user: User,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get analytics for a specific document."""
    return await get_document_analytics(document_id, user.id, start_date, end_date, db)


async def get_user_analytics_endpoint(
    user: User,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get analytics for a specific user."""
    return await get_user_analytics(user.id, start_date, end_date, db)


async def get_organization_analytics_endpoint(
    organization_id: str,
    user: User,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get analytics for an organization."""
    return await get_organization_analytics(organization_id, user.id, start_date, end_date, db)


async def get_system_analytics_endpoint(
    user: User,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get system-wide analytics (admin only)."""
    return await get_system_analytics(user.id, start_date, end_date, db)


async def get_ai_usage_analytics_endpoint(
    user: User,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get AI usage analytics for user."""
    return await get_ai_usage_analytics(user.id, start_date, end_date, db)


# Route definitions
@router.get("/documents/{document_id}", response_model=Dict[str, Any])
async def get_document_analytics_route(
    document_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics for a specific document."""
    return await get_document_analytics_endpoint(document_id, current_user, start_date, end_date, db)


@router.get("/users/me", response_model=Dict[str, Any])
async def get_user_analytics_route(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics for current user."""
    return await get_user_analytics_endpoint(current_user, start_date, end_date, db)


@router.get("/organizations/{organization_id}", response_model=Dict[str, Any])
async def get_organization_analytics_route(
    organization_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics for an organization."""
    return await get_organization_analytics_endpoint(organization_id, current_user, start_date, end_date, db)


@router.get("/system", response_model=Dict[str, Any])
async def get_system_analytics_route(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get system-wide analytics (admin only)."""
    return await get_system_analytics_endpoint(current_user, start_date, end_date, db)


@router.get("/ai/usage", response_model=Dict[str, Any])
async def get_ai_usage_analytics_route(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI usage analytics for current user."""
    return await get_ai_usage_analytics_endpoint(current_user, start_date, end_date, db)


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_analytics_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard analytics for current user."""
    # Get user analytics for last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    user_analytics = await get_user_analytics_endpoint(current_user, start_date, end_date, db)
    
    # Get AI usage analytics for last 30 days
    ai_analytics = await get_ai_usage_analytics_endpoint(current_user, start_date, end_date, db)
    
    # Get recent documents
    from app.services.document_service import list_documents
    recent_docs = await list_documents(current_user.id, page=1, size=5, db=db)
    
    return {
        "user_analytics": user_analytics,
        "ai_analytics": ai_analytics,
        "recent_documents": recent_docs.get("documents", []),
        "summary": {
            "total_documents": user_analytics["metrics"]["total_documents"],
            "total_ai_requests": ai_analytics["metrics"]["total_requests"],
            "total_collaboration_events": user_analytics["metrics"]["total_events"],
            "last_activity": user_analytics["last_activity"]
        }
    }


@router.get("/reports/daily", response_model=Dict[str, Any])
async def get_daily_report_route(
    date: Optional[datetime] = Query(None, description="Date for daily report"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get daily analytics report."""
    if not date:
        date = datetime.utcnow().date()
    
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())
    
    user_analytics = await get_user_analytics_endpoint(current_user, start_date, end_date, db)
    ai_analytics = await get_ai_usage_analytics_endpoint(current_user, start_date, end_date, db)
    
    return {
        "date": date.isoformat(),
        "user_analytics": user_analytics,
        "ai_analytics": ai_analytics,
        "summary": {
            "documents_created": user_analytics["metrics"]["total_documents"],
            "ai_requests": ai_analytics["metrics"]["total_requests"],
            "collaboration_events": user_analytics["metrics"]["total_events"],
            "ai_cost": ai_analytics["metrics"]["total_cost"]
        }
    }


@router.get("/reports/weekly", response_model=Dict[str, Any])
async def get_weekly_report_route(
    week_start: Optional[datetime] = Query(None, description="Week start date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get weekly analytics report."""
    if not week_start:
        # Get start of current week
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
    
    start_date = datetime.combine(week_start, datetime.min.time())
    end_date = start_date + timedelta(days=7)
    
    user_analytics = await get_user_analytics_endpoint(current_user, start_date, end_date, db)
    ai_analytics = await get_ai_usage_analytics_endpoint(current_user, start_date, end_date, db)
    
    return {
        "week_start": week_start.isoformat(),
        "week_end": (week_start + timedelta(days=6)).isoformat(),
        "user_analytics": user_analytics,
        "ai_analytics": ai_analytics,
        "summary": {
            "documents_created": user_analytics["metrics"]["total_documents"],
            "ai_requests": ai_analytics["metrics"]["total_requests"],
            "collaboration_events": user_analytics["metrics"]["total_events"],
            "ai_cost": ai_analytics["metrics"]["total_cost"]
        }
    }


@router.get("/reports/monthly", response_model=Dict[str, Any])
async def get_monthly_report_route(
    month: Optional[int] = Query(None, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get monthly analytics report."""
    if not month or not year:
        now = datetime.utcnow()
        month = now.month
        year = now.year
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    user_analytics = await get_user_analytics_endpoint(current_user, start_date, end_date, db)
    ai_analytics = await get_ai_usage_analytics_endpoint(current_user, start_date, end_date, db)
    
    return {
        "month": month,
        "year": year,
        "user_analytics": user_analytics,
        "ai_analytics": ai_analytics,
        "summary": {
            "documents_created": user_analytics["metrics"]["total_documents"],
            "ai_requests": ai_analytics["metrics"]["total_requests"],
            "collaboration_events": user_analytics["metrics"]["total_events"],
            "ai_cost": ai_analytics["metrics"]["total_cost"]
        }
    }


@router.get("/export/{report_type}")
async def export_analytics_report_route(
    report_type: str,
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    format: str = Query("json", description="Export format (json, csv, pdf)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Export analytics report in specified format."""
    # This would implement report export logic
    # For now, returning a placeholder response
    return {
        "report_type": report_type,
        "format": format,
        "download_url": f"/api/v1/analytics/export/{report_type}?format={format}",
        "expires_at": "2023-12-31T23:59:59Z"
    }




