"""API routes"""

from fastapi import APIRouter, HTTPException
from src.services.user_service import UserService
from src.models.user_model import UserCreate, UserResponse

router = APIRouter()

@router.get("/users")
async def get_users():
    """Get all users"""
    try:
        users = await UserService.get_all_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users")
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        new_user = await UserService.create_user(user)
        return {"user": new_user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
