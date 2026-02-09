"""User service"""

from src.models.user_model import UserCreate, UserResponse

class UserService:
    """User service for business logic"""
    
    @staticmethod
    async def get_all_users():
        """Get all users"""
        # TODO: Implement database query
        return []
    
    @staticmethod
    async def create_user(user: UserCreate):
        """Create a new user"""
        # TODO: Implement user creation
        return UserResponse(id=1, **user.dict())
