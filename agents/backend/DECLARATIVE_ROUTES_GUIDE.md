# Declarative Route Definitions with Clear Return Type Annotations
## Complete Guide for FastAPI Applications

### 📋 Overview

This guide demonstrates how to implement **declarative route definitions** with **clear return type annotations** in FastAPI applications. This approach provides:

- **Type Safety**: Full type checking throughout the request/response cycle
- **Clear Documentation**: Self-documenting routes with comprehensive metadata
- **Performance Monitoring**: Built-in metrics and performance tracking
- **Error Handling**: Structured error responses with proper HTTP status codes
- **OpenAPI Integration**: Automatic API documentation generation
- **Maintainability**: Consistent patterns across all routes

### 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Declarative   │    │   Type-Safe      │    ┌   Performance   │
│   Route         │───▶│   Request/       │───▶│   Monitoring    │
│   Decorator     │    │   Response       │    │   & Metrics     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenAPI       │    │   Error          │    │   Logging &     │
│   Documentation │    │   Handling       │    │   Tracing       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🚀 Core Concepts

#### **1. Declarative Route Decorators**

Declarative route decorators provide a clean, self-documenting way to define API endpoints:

```python
@get_route(
    path="/users",
    response_model=UserListResponse,
    tags=["users"],
    summary="Get all users",
    description="Retrieve a paginated list of all users in the system"
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page")
) -> UserListResponse:
    """Get all users with pagination."""
    # Implementation here
    pass
```

#### **2. Clear Return Type Annotations**

Every route function has explicit return type annotations:

```python
async def create_user(
    user_data: UserCreateRequest = Body(...)
) -> UserResponse:
    """
    Create a new user.
    
    Returns:
        UserResponse: Created user information
    """
    # Implementation here
    pass
```

#### **3. Structured Response Models**

All responses use structured Pydantic models:

```python
class UserResponse(BaseResponseModel):
    """Response model for user operations."""
    
    success: bool = Field(default=True)
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    age: Optional[int] = Field(None, description="User age")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Computed display name."""
        return f"{self.name} ({self.email})"
```

### 📦 Installation and Setup

#### **1. Import Required Modules**

```python
from onyx.server.features.core.declarative_routes import (
    get_route, post_route, put_route, delete_route, patch_route,
    BaseResponseModel, SuccessResponse, ErrorResponse, PaginatedResponse,
    DeclarativeRouter
)
```

#### **2. Create Base Response Models**

```python
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional, List, Dict, Any

class BaseResponseModel(OptimizedBaseModel):
    """Base response model for all API endpoints."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    execution_time_ms: Optional[float] = Field(None, description="Execution time")
```

### 🎯 Creating Declarative Routes

#### **1. GET Routes**

```python
@get_route(
    path="/users",
    response_model=UserListResponse,
    tags=["users"],
    summary="Get all users",
    description="Retrieve a paginated list of all users in the system"
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query("name", description="Sort field"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order")
) -> UserListResponse:
    """
    Get all users with pagination and filtering.
    
    Args:
        page: Page number for pagination
        per_page: Number of items per page
        search: Optional search term
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        UserListResponse: Paginated list of users
    """
    try:
        # Implementation here
        users = await user_service.get_users(
            page=page,
            per_page=per_page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return UserListResponse(
            success=True,
            data=users.items,
            pagination={
                "page": page,
                "per_page": per_page,
                "total": users.total,
                "pages": users.pages,
                "has_next": users.has_next,
                "has_prev": users.has_prev
            }
        )
        
    except Exception as e:
        return UserListResponse(
            success=False,
            error=str(e),
            data=[],
            pagination={}
        )
```

#### **2. POST Routes**

```python
@post_route(
    path="/users",
    response_model=UserResponse,
    status_code=201,
    tags=["users"],
    summary="Create new user",
    description="Create a new user in the system"
)
async def create_user(
    user_data: UserCreateRequest = Body(..., description="User data")
) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        
    Returns:
        UserResponse: Created user information
    """
    try:
        # Validate and create user
        user = await user_service.create_user(user_data)
        
        return UserResponse(
            success=True,
            user_id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            created_at=user.created_at
        )
        
    except ValidationError as e:
        return UserResponse(
            success=False,
            error=f"Validation error: {str(e)}",
            user_id="",
            name="",
            email=""
        )
    except Exception as e:
        return UserResponse(
            success=False,
            error=f"Failed to create user: {str(e)}",
            user_id="",
            name="",
            email=""
        )
```

#### **3. PUT Routes**

```python
@put_route(
    path="/users/{user_id}",
    response_model=UserResponse,
    tags=["users"],
    summary="Update user",
    description="Update an existing user's information"
)
async def update_user(
    user_id: str = Path(..., description="User ID"),
    user_data: UserCreateRequest = Body(..., description="Updated user data")
) -> UserResponse:
    """
    Update an existing user.
    
    Args:
        user_id: The ID of the user to update
        user_data: Updated user data
        
    Returns:
        UserResponse: Updated user information
    """
    try:
        # Update user
        user = await user_service.update_user(user_id, user_data)
        
        return UserResponse(
            success=True,
            user_id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            updated_at=user.updated_at
        )
        
    except ResourceNotFoundError:
        return UserResponse(
            success=False,
            error=f"User {user_id} not found",
            user_id=user_id,
            name="",
            email=""
        )
    except Exception as e:
        return UserResponse(
            success=False,
            error=f"Failed to update user: {str(e)}",
            user_id=user_id,
            name="",
            email=""
        )
```

#### **4. DELETE Routes**

```python
@delete_route(
    path="/users/{user_id}",
    response_model=SuccessResponse,
    status_code=204,
    tags=["users"],
    summary="Delete user",
    description="Delete a user from the system"
)
async def delete_user(
    user_id: str = Path(..., description="User ID")
) -> SuccessResponse:
    """
    Delete a user.
    
    Args:
        user_id: The ID of the user to delete
        
    Returns:
        SuccessResponse: Deletion confirmation
    """
    try:
        # Delete user
        await user_service.delete_user(user_id)
        
        return SuccessResponse(
            success=True,
            message=f"User {user_id} deleted successfully"
        )
        
    except ResourceNotFoundError:
        return SuccessResponse(
            success=False,
            error=f"User {user_id} not found"
        )
    except Exception as e:
        return SuccessResponse(
            success=False,
            error=f"Failed to delete user: {str(e)}"
        )
```

#### **5. PATCH Routes**

```python
@patch_route(
    path="/users/{user_id}",
    response_model=UserResponse,
    tags=["users"],
    summary="Partially update user",
    description="Partially update an existing user's information"
)
async def patch_user(
    user_id: str = Path(..., description="User ID"),
    updates: Dict[str, Any] = Body(..., description="Partial updates")
) -> UserResponse:
    """
    Partially update a user.
    
    Args:
        user_id: The ID of the user to update
        updates: Partial updates to apply
        
    Returns:
        UserResponse: Updated user information
    """
    try:
        # Apply partial updates
        user = await user_service.patch_user(user_id, updates)
        
        return UserResponse(
            success=True,
            user_id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            updated_at=user.updated_at
        )
        
    except Exception as e:
        return UserResponse(
            success=False,
            error=f"Failed to update user: {str(e)}",
            user_id=user_id,
            name="",
            email=""
        )
```

### 🔧 Route Decorator Options

#### **1. Basic Options**

```python
@get_route(
    path="/users",                    # Route path
    response_model=UserListResponse,  # Response model for validation
    status_code=200,                  # HTTP status code
    tags=["users"],                   # OpenAPI tags
    summary="Get all users",          # Short description
    description="Detailed description", # Long description
    deprecated=False,                 # Mark as deprecated
    include_in_schema=True           # Include in OpenAPI schema
)
```

#### **2. Advanced Options**

```python
@post_route(
    path="/users",
    response_model=UserResponse,
    status_code=201,
    tags=["users"],
    summary="Create new user",
    description="Create a new user in the system",
    dependencies=[require_auth, require_permission("create_user")],  # Dependencies
    cache_result=True,               # Cache response
    cache_ttl=300,                   # Cache TTL in seconds
    log_execution=True,              # Log execution details
    monitor_performance=True         # Monitor performance
)
```

### 📊 Response Models

#### **1. Base Response Model**

```python
class BaseResponseModel(OptimizedBaseModel):
    """Base response model for all API endpoints."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    execution_time_ms: Optional[float] = Field(None, description="Execution time")
```

#### **2. Success Response**

```python
class SuccessResponse(BaseResponseModel):
    """Standard success response."""
    
    success: bool = Field(default=True)
    message: Optional[str] = Field(None, description="Success message")
```

#### **3. Error Response**

```python
class ErrorResponse(BaseResponseModel):
    """Standard error response."""
    
    success: bool = Field(default=False)
    error_code: str = Field(..., description="Error code for programmatic handling")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    suggestions: Optional[List[str]] = Field(None, description="Suggested solutions")
```

#### **4. Paginated Response**

```python
class PaginatedResponse(BaseResponseModel, Generic[ResponseT]):
    """Paginated response wrapper."""
    
    success: bool = Field(default=True)
    data: List[ResponseT] = Field(..., description="List of items")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    
    @computed_field
    @property
    def total_count(self) -> int:
        """Total number of items."""
        return self.pagination.get("total", 0)
    
    @computed_field
    @property
    def page_count(self) -> int:
        """Total number of pages."""
        return self.pagination.get("pages", 0)
```

### 🏗️ Request Models

#### **1. Create Request Model**

```python
class UserCreateRequest(BaseModel):
    """Request model for user creation."""
    
    name: str = Field(..., min_length=1, max_length=100, description="User name")
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", description="User email")
    age: Optional[int] = Field(None, ge=0, le=150, description="User age")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean name."""
        return v.strip().title()
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email."""
        return v.strip().lower()
```

#### **2. Update Request Model**

```python
class UserUpdateRequest(BaseModel):
    """Request model for user updates."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User name")
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$", description="User email")
    age: Optional[int] = Field(None, ge=0, le=150, description="User age")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    
    @model_validator(mode='before')
    @classmethod
    def validate_at_least_one_field(cls, values):
        """Ensure at least one field is provided for update."""
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values
```

### 📈 Performance Monitoring

#### **1. Route Metrics**

```python
from onyx.server.features.core.declarative_routes import get_route_metrics

# Get all route metrics
metrics = get_route_metrics()

for route_key, route_metrics in metrics.items():
    print(f"Route: {route_key}")
    print(f"  Executions: {route_metrics['execution_count']}")
    print(f"  Success Rate: {route_metrics['success_count'] / route_metrics['execution_count']:.2%}")
    print(f"  Avg Time: {route_metrics['total_execution_time'] / route_metrics['execution_count']:.3f}ms")
```

#### **2. Metrics Endpoint**

```python
@get_route(
    path="/metrics",
    response_model=Dict[str, Any],
    tags=["monitoring"],
    summary="Get route metrics",
    description="Get performance metrics for all routes"
)
async def get_metrics() -> Dict[str, Any]:
    """
    Get route performance metrics.
    
    Returns:
        Dict[str, Any]: Route metrics
    """
    return {
        "route_metrics": get_route_metrics(),
        "timestamp": datetime.utcnow().isoformat(),
        "total_routes": len(get_route_metrics())
    }
```

### 🔄 Router Integration

#### **1. Declarative Router**

```python
from onyx.server.features.core.declarative_routes import DeclarativeRouter

# Create router
router = DeclarativeRouter(prefix="/api/v1", tags=["api"])

# Register routes
router.register_route(
    RouteMetadata(
        path="/users",
        method="GET",
        tags=["users"],
        summary="Get all users",
        description="Retrieve a paginated list of all users",
        response_model=UserListResponse,
        status_code=200
    ),
    get_users
)

# Get FastAPI router
fastapi_router = router.get_router()
```

#### **2. FastAPI App Integration**

```python
from fastapi import FastAPI
from onyx.server.features.core.declarative_routes import declarative_router

app = FastAPI(title="My API", version="1.0.0")

# Include declarative router
app.include_router(declarative_router.get_router())

# Or include individual routes
app.include_router(get_users.router)
```

### 🧪 Testing Declarative Routes

#### **1. Unit Testing**

```python
import pytest
from fastapi.testclient import TestClient
from onyx.server.features.core.declarative_routes import get_users, create_user

def test_get_users_success():
    """Test successful user retrieval."""
    # Mock dependencies
    with patch('user_service.get_users') as mock_get_users:
        mock_get_users.return_value = MockUsers(
            items=[MockUser(id="1", name="John", email="john@example.com")],
            total=1,
            pages=1,
            has_next=False,
            has_prev=False
        )
        
        # Test route
        result = get_users(page=1, per_page=10)
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0].name == "John"

def test_create_user_validation_error():
    """Test user creation with validation error."""
    user_data = UserCreateRequest(
        name="",  # Invalid: empty name
        email="invalid-email",  # Invalid: wrong format
        age=200  # Invalid: too old
    )
    
    result = create_user(user_data)
    
    assert result.success is False
    assert "validation error" in result.error.lower()
```

#### **2. Integration Testing**

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_users_endpoint(async_client: AsyncClient):
    """Test GET /users endpoint."""
    response = await async_client.get("/api/v1/users?page=1&per_page=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "pagination" in data

@pytest.mark.asyncio
async def test_create_user_endpoint(async_client: AsyncClient):
    """Test POST /users endpoint."""
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30
    }
    
    response = await async_client.post("/api/v1/users", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"
```

### 🔒 Error Handling

#### **1. Structured Error Responses**

```python
@get_route(
    path="/users/{user_id}",
    response_model=UserResponse,
    tags=["users"]
)
async def get_user(user_id: str = Path(...)) -> UserResponse:
    """Get user by ID with comprehensive error handling."""
    try:
        user = await user_service.get_user(user_id)
        
        if not user:
            return UserResponse(
                success=False,
                error=f"User {user_id} not found",
                error_code="USER_NOT_FOUND",
                user_id=user_id,
                name="",
                email=""
            )
        
        return UserResponse(
            success=True,
            user_id=user.id,
            name=user.name,
            email=user.email,
            age=user.age
        )
        
    except ValidationError as e:
        return UserResponse(
            success=False,
            error=f"Validation error: {str(e)}",
            error_code="VALIDATION_ERROR",
            user_id=user_id,
            name="",
            email=""
        )
    except PermissionError as e:
        return UserResponse(
            success=False,
            error=f"Permission denied: {str(e)}",
            error_code="PERMISSION_DENIED",
            user_id=user_id,
            name="",
            email=""
        )
    except Exception as e:
        return UserResponse(
            success=False,
            error=f"Internal server error: {str(e)}",
            error_code="INTERNAL_ERROR",
            user_id=user_id,
            name="",
            email=""
        )
```

#### **2. HTTP Status Code Mapping**

```python
def map_error_to_status_code(error_response: BaseResponseModel) -> int:
    """Map error response to appropriate HTTP status code."""
    error_code = getattr(error_response, 'error_code', 'UNKNOWN_ERROR')
    
    status_code_map = {
        'VALIDATION_ERROR': 400,
        'USER_NOT_FOUND': 404,
        'PERMISSION_DENIED': 403,
        'AUTHENTICATION_ERROR': 401,
        'RATE_LIMIT_ERROR': 429,
        'INTERNAL_ERROR': 500
    }
    
    return status_code_map.get(error_code, 500)
```

### 🚀 Best Practices

#### **1. Route Organization**

```python
# ✅ Good: Organized by resource
@get_route("/users", tags=["users"])
async def get_users() -> UserListResponse:
    pass

@post_route("/users", tags=["users"])
async def create_user() -> UserResponse:
    pass

@get_route("/users/{user_id}", tags=["users"])
async def get_user() -> UserResponse:
    pass

# ❌ Bad: Mixed resources
@get_route("/users")
async def get_users() -> UserListResponse:
    pass

@post_route("/create-user")  # Inconsistent naming
async def create_user() -> UserResponse:
    pass
```

#### **2. Response Models**

```python
# ✅ Good: Specific response models
class UserResponse(BaseResponseModel):
    user_id: str = Field(...)
    name: str = Field(...)
    email: str = Field(...)

# ❌ Bad: Generic response
class GenericResponse(BaseResponseModel):
    data: Dict[str, Any] = Field(...)  # Too generic
```

#### **3. Error Handling**

```python
# ✅ Good: Specific error handling
try:
    user = await user_service.get_user(user_id)
    if not user:
        return UserResponse(
            success=False,
            error=f"User {user_id} not found",
            error_code="USER_NOT_FOUND"
        )
    return UserResponse(success=True, **user.dict())
except ValidationError as e:
    return UserResponse(
        success=False,
        error=str(e),
        error_code="VALIDATION_ERROR"
    )

# ❌ Bad: Generic error handling
try:
    user = await user_service.get_user(user_id)
    return UserResponse(success=True, **user.dict())
except Exception as e:
    return UserResponse(success=False, error=str(e))
```

#### **4. Type Annotations**

```python
# ✅ Good: Clear type annotations
async def create_user(
    user_data: UserCreateRequest = Body(...)
) -> UserResponse:
    """Create a new user."""
    pass

# ❌ Bad: Missing type annotations
async def create_user(user_data):
    """Create a new user."""
    pass
```

### 📋 Complete Example

Here's a complete example showing how to implement declarative routes:

```python
# models.py
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import List, Optional

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: Optional[int] = Field(None, ge=0, le=150)

class UserResponse(BaseResponseModel):
    user_id: str = Field(...)
    name: str = Field(...)
    email: str = Field(...)
    age: Optional[int] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.email})"

class UserListResponse(PaginatedResponse[UserResponse]):
    pass

# routes.py
@get_route(
    path="/users",
    response_model=UserListResponse,
    tags=["users"],
    summary="Get all users",
    description="Retrieve a paginated list of all users"
)
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
) -> UserListResponse:
    """Get all users with pagination."""
    try:
        users = await user_service.get_users(page=page, per_page=per_page)
        
        return UserListResponse(
            success=True,
            data=users.items,
            pagination={
                "page": page,
                "per_page": per_page,
                "total": users.total,
                "pages": users.pages,
                "has_next": users.has_next,
                "has_prev": users.has_prev
            }
        )
    except Exception as e:
        return UserListResponse(
            success=False,
            error=str(e),
            data=[],
            pagination={}
        )

@post_route(
    path="/users",
    response_model=UserResponse,
    status_code=201,
    tags=["users"],
    summary="Create new user"
)
async def create_user(
    user_data: UserCreateRequest = Body(...)
) -> UserResponse:
    """Create a new user."""
    try:
        user = await user_service.create_user(user_data)
        
        return UserResponse(
            success=True,
            user_id=user.id,
            name=user.name,
            email=user.email,
            age=user.age
        )
    except Exception as e:
        return UserResponse(
            success=False,
            error=str(e),
            user_id="",
            name="",
            email=""
        )

# main.py
from fastapi import FastAPI
from onyx.server.features.core.declarative_routes import DeclarativeRouter

app = FastAPI(title="User API", version="1.0.0")

# Create and register router
router = DeclarativeRouter(prefix="/api/v1", tags=["api"])
router.register_route(get_users._route_metadata, get_users)
router.register_route(create_user._route_metadata, create_user)

app.include_router(router.get_router())
```

### 🎯 Benefits of This Approach

1. **Type Safety**: Full type checking throughout the request/response cycle
2. **Clear Documentation**: Self-documenting routes with comprehensive metadata
3. **Performance Monitoring**: Built-in metrics and performance tracking
4. **Error Handling**: Structured error responses with proper HTTP status codes
5. **OpenAPI Integration**: Automatic API documentation generation
6. **Maintainability**: Consistent patterns across all routes
7. **Testability**: Easy to test with clear input/output contracts
8. **Scalability**: Easy to add new routes following established patterns
9. **Monitoring**: Built-in performance metrics and error tracking
10. **Consistency**: Standardized response formats across all endpoints

This declarative approach with clear return type annotations provides a robust, maintainable, and type-safe foundation for building FastAPI applications. 