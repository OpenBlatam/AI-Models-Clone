# Synchronous vs Asynchronous Function Definitions
## Complete Guide for FastAPI Applications

### 📋 Overview

This guide demonstrates the proper use of **`def` for synchronous operations** and **`async def` for asynchronous operations** in FastAPI applications. Understanding when to use each type is crucial for performance, scalability, and maintainability.

### 🎯 Key Principles

#### **1. Use `def` for Synchronous Operations**
- CPU-bound computations
- Simple data transformations
- File I/O operations (when not blocking)
- Configuration and setup
- Utility functions
- Validation logic

#### **2. Use `async def` for Asynchronous Operations**
- Database operations
- HTTP requests
- File I/O operations (when blocking)
- External API calls
- Background tasks
- Event-driven operations

### 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Synchronous   │    │   Asynchronous   │    ┌   Hybrid        │
│   Operations    │    │   Operations      │    │   Operations    │
│   (def)         │    │   (async def)     │    │   (mixed)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CPU-bound     │    │   I/O-bound      │    │   Orchestration │
│   computations  │    │   operations     │    │   & Coordination │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🚀 Core Concepts

#### **1. Synchronous Functions (`def`)**

Synchronous functions execute in a blocking manner and are suitable for operations that don't involve waiting for external resources.

```python
def calculate_user_score(user_data: Dict[str, Any]) -> float:
    """
    Calculate user score based on various metrics.
    
    Args:
        user_data: User data dictionary
        
    Returns:
        float: Calculated score
    """
    # CPU-bound computation
    engagement_score = user_data.get('engagement', 0) * 0.3
    activity_score = user_data.get('activity', 0) * 0.4
    quality_score = user_data.get('quality', 0) * 0.3
    
    return engagement_score + activity_score + quality_score

def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return bool(re.match(pattern, email))

def format_user_display_name(first_name: str, last_name: str) -> str:
    """
    Format user display name.
    
    Args:
        first_name: User's first name
        last_name: User's last name
        
    Returns:
        str: Formatted display name
    """
    return f"{first_name.strip().title()} {last_name.strip().title()}"
```

#### **2. Asynchronous Functions (`async def`)**

Asynchronous functions are suitable for operations that involve waiting for external resources like databases, APIs, or file systems.

```python
async def fetch_user_from_database(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user data from database asynchronously.
    
    Args:
        user_id: User ID to fetch
        
    Returns:
        Optional[Dict[str, Any]]: User data or None if not found
    """
    try:
        # Database operation (I/O-bound)
        async with get_database_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                return user.to_dict()
            return None
            
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {str(e)}")
        return None

async def call_external_api(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call external API asynchronously.
    
    Args:
        endpoint: API endpoint URL
        data: Request data
        
    Returns:
        Dict[str, Any]: API response
    """
    try:
        # HTTP request (I/O-bound)
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        logger.error(f"API call failed: {str(e)}")
        raise

async def process_file_upload(file_path: str) -> Dict[str, Any]:
    """
    Process uploaded file asynchronously.
    
    Args:
        file_path: Path to uploaded file
        
    Returns:
        Dict[str, Any]: Processing results
    """
    try:
        # File I/O operation (I/O-bound)
        async with aiofiles.open(file_path, 'r') as file:
            content = await file.read()
            
        # Process content
        result = await analyze_file_content(content)
        return result
        
    except Exception as e:
        logger.error(f"File processing failed: {str(e)}")
        raise
```

### 📦 Installation and Setup

#### **1. Required Dependencies**

```python
# For async operations
import asyncio
import aiofiles
import httpx
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# For sync operations
import re
import json
import hashlib
from typing import Dict, List, Optional, Any
```

#### **2. Database Setup**

```python
# Async database setup
async def setup_database():
    """Setup async database connection."""
    engine = create_async_engine(
        "postgresql+asyncpg://user:password@localhost/dbname",
        echo=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    return engine

# Sync database utilities
def create_connection_string(config: Dict[str, str]) -> str:
    """Create database connection string synchronously."""
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
```

### 🎯 Creating Proper Function Definitions

#### **1. Synchronous Route Handlers**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserRequest(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

@app.get("/users/validate")
def validate_user_data(user: UserRequest) -> Dict[str, Any]:
    """
    Validate user data synchronously.
    
    Args:
        user: User data to validate
        
    Returns:
        Dict[str, Any]: Validation results
    """
    # Synchronous validation
    errors = []
    
    if not validate_email_format(user.email):
        errors.append("Invalid email format")
    
    if user.age is not None and (user.age < 0 or user.age > 150):
        errors.append("Invalid age")
    
    if len(user.name.strip()) < 2:
        errors.append("Name too short")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "user": user.dict()
    }

@app.post("/users/calculate-score")
def calculate_user_profile_score(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate user profile score synchronously.
    
    Args:
        user_data: User data for scoring
        
    Returns:
        Dict[str, Any]: Score and breakdown
    """
    # CPU-bound calculations
    engagement_score = calculate_engagement_score(user_data)
    activity_score = calculate_activity_score(user_data)
    quality_score = calculate_quality_score(user_data)
    
    total_score = engagement_score + activity_score + quality_score
    
    return {
        "total_score": total_score,
        "breakdown": {
            "engagement": engagement_score,
            "activity": activity_score,
            "quality": quality_score
        },
        "grade": get_score_grade(total_score)
    }
```

#### **2. Asynchronous Route Handlers**

```python
@app.get("/users/{user_id}")
async def get_user(user_id: str) -> Dict[str, Any]:
    """
    Get user by ID asynchronously.
    
    Args:
        user_id: User ID to fetch
        
    Returns:
        Dict[str, Any]: User data
    """
    # Database operation (I/O-bound)
    user_data = await fetch_user_from_database(user_id)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Enrich with additional data
    user_data["profile_score"] = await calculate_user_profile_score_async(user_data)
    user_data["recent_activity"] = await fetch_recent_activity(user_id)
    
    return user_data

@app.post("/users")
async def create_user(user_request: UserRequest) -> Dict[str, Any]:
    """
    Create new user asynchronously.
    
    Args:
        user_request: User creation data
        
    Returns:
        Dict[str, Any]: Created user data
    """
    # Validate input synchronously
    validation_result = validate_user_data(user_request)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400, 
            detail={"message": "Validation failed", "errors": validation_result["errors"]}
        )
    
    # Check if user exists (I/O-bound)
    existing_user = await check_user_exists(user_request.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    # Create user (I/O-bound)
    user_data = await create_user_in_database(user_request.dict())
    
    # Send welcome email (I/O-bound)
    await send_welcome_email(user_data["email"])
    
    # Update analytics (I/O-bound)
    await update_user_analytics(user_data["id"])
    
    return user_data

@app.get("/users/{user_id}/analytics")
async def get_user_analytics(user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive user analytics asynchronously.
    
    Args:
        user_id: User ID
        
    Returns:
        Dict[str, Any]: Analytics data
    """
    # Parallel async operations
    user_data, activity_data, engagement_data = await asyncio.gather(
        fetch_user_from_database(user_id),
        fetch_user_activity(user_id),
        fetch_user_engagement(user_id)
    )
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Synchronous data processing
    analytics = process_analytics_data(user_data, activity_data, engagement_data)
    
    return analytics
```

#### **3. Hybrid Functions (Mixed Sync/Async)**

```python
async def process_user_registration(user_request: UserRequest) -> Dict[str, Any]:
    """
    Process user registration with mixed sync/async operations.
    
    Args:
        user_request: User registration data
        
    Returns:
        Dict[str, Any]: Registration results
    """
    # Synchronous validation
    validation_result = validate_user_data(user_request)
    if not validation_result["valid"]:
        return {
            "success": False,
            "errors": validation_result["errors"]
        }
    
    # Synchronous data preparation
    user_data = prepare_user_data(user_request)
    user_data["registration_date"] = datetime.utcnow()
    
    # Asynchronous database operations
    try:
        created_user = await create_user_in_database(user_data)
        
        # Parallel async operations
        await asyncio.gather(
            send_welcome_email(created_user["email"]),
            update_registration_analytics(),
            create_user_profile(created_user["id"])
        )
        
        return {
            "success": True,
            "user": created_user,
            "message": "User registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return {
            "success": False,
            "error": "Registration failed"
        }

def prepare_user_data(user_request: UserRequest) -> Dict[str, Any]:
    """
    Prepare user data for database insertion (synchronous).
    
    Args:
        user_request: User request data
        
    Returns:
        Dict[str, Any]: Prepared user data
    """
    return {
        "name": format_user_display_name(user_request.name, ""),
        "email": user_request.email.lower().strip(),
        "age": user_request.age,
        "created_at": datetime.utcnow(),
        "status": "active"
    }
```

### 🔧 Utility Functions

#### **1. Synchronous Utilities**

```python
def calculate_engagement_score(user_data: Dict[str, Any]) -> float:
    """Calculate user engagement score (synchronous)."""
    likes = user_data.get('likes', 0)
    comments = user_data.get('comments', 0)
    shares = user_data.get('shares', 0)
    
    return (likes * 0.4) + (comments * 0.4) + (shares * 0.2)

def calculate_activity_score(user_data: Dict[str, Any]) -> float:
    """Calculate user activity score (synchronous)."""
    posts = user_data.get('posts', 0)
    login_frequency = user_data.get('login_frequency', 0)
    
    return (posts * 0.6) + (login_frequency * 0.4)

def calculate_quality_score(user_data: Dict[str, Any]) -> float:
    """Calculate user quality score (synchronous)."""
    profile_completeness = user_data.get('profile_completeness', 0)
    verification_status = user_data.get('verified', False)
    
    base_score = profile_completeness * 0.7
    bonus = 30 if verification_status else 0
    
    return min(base_score + bonus, 100)

def get_score_grade(score: float) -> str:
    """Get letter grade based on score (synchronous)."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def validate_email_format(email: str) -> bool:
    """Validate email format (synchronous)."""
    import re
    pattern = r'^[^@]+@[^@]+\.[^@]+$'
    return bool(re.match(pattern, email))

def format_user_display_name(first_name: str, last_name: str) -> str:
    """Format user display name (synchronous)."""
    return f"{first_name.strip().title()} {last_name.strip().title()}"
```

#### **2. Asynchronous Utilities**

```python
async def fetch_user_from_database(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user from database (asynchronous)."""
    try:
        async with get_database_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            return user.to_dict() if user else None
    except Exception as e:
        logger.error(f"Database fetch failed: {str(e)}")
        return None

async def create_user_in_database(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create user in database (asynchronous)."""
    try:
        async with get_database_session() as session:
            user = User(**user_data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user.to_dict()
    except Exception as e:
        logger.error(f"User creation failed: {str(e)}")
        raise

async def check_user_exists(email: str) -> bool:
    """Check if user exists (asynchronous)."""
    try:
        async with get_database_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none() is not None
    except Exception as e:
        logger.error(f"User existence check failed: {str(e)}")
        return False

async def send_welcome_email(email: str) -> bool:
    """Send welcome email (asynchronous)."""
    try:
        # Simulate email sending
        await asyncio.sleep(0.1)
        logger.info(f"Welcome email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return False

async def update_user_analytics(user_id: str) -> bool:
    """Update user analytics (asynchronous)."""
    try:
        # Simulate analytics update
        await asyncio.sleep(0.05)
        logger.info(f"Analytics updated for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Analytics update failed: {str(e)}")
        return False

async def fetch_user_activity(user_id: str) -> List[Dict[str, Any]]:
    """Fetch user activity (asynchronous)."""
    try:
        async with get_database_session() as session:
            result = await session.execute(
                select(UserActivity).where(UserActivity.user_id == user_id)
            )
            activities = result.scalars().all()
            return [activity.to_dict() for activity in activities]
    except Exception as e:
        logger.error(f"Activity fetch failed: {str(e)}")
        return []

async def fetch_user_engagement(user_id: str) -> Dict[str, Any]:
    """Fetch user engagement data (asynchronous)."""
    try:
        async with get_database_session() as session:
            result = await session.execute(
                select(UserEngagement).where(UserEngagement.user_id == user_id)
            )
            engagement = result.scalar_one_or_none()
            return engagement.to_dict() if engagement else {}
    except Exception as e:
        logger.error(f"Engagement fetch failed: {str(e)}")
        return {}
```

### 📊 Performance Considerations

#### **1. When to Use Synchronous Functions**

```python
# ✅ Good: CPU-bound operations
def calculate_complex_algorithm(data: List[float]) -> float:
    """Complex mathematical computation."""
    return sum(x ** 2 for x in data) / len(data)

# ✅ Good: Simple data transformations
def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount."""
    return f"{currency} {amount:.2f}"

# ✅ Good: Validation logic
def validate_user_input(data: Dict[str, Any]) -> List[str]:
    """Validate user input data."""
    errors = []
    if not data.get('name'):
        errors.append("Name is required")
    if not data.get('email'):
        errors.append("Email is required")
    return errors

# ❌ Bad: I/O operations in sync functions
def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """This should be async!"""
    # Database call - should be async
    user = database.get_user(user_id)  # Blocking!
    return user
```

#### **2. When to Use Asynchronous Functions**

```python
# ✅ Good: Database operations
async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user from database."""
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

# ✅ Good: HTTP requests
async def fetch_external_data(url: str) -> Dict[str, Any]:
    """Fetch data from external API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ✅ Good: File operations
async def read_large_file(file_path: str) -> str:
    """Read large file asynchronously."""
    async with aiofiles.open(file_path, 'r') as file:
        return await file.read()

# ❌ Bad: CPU-bound operations in async functions
async def calculate_simple_sum(numbers: List[int]) -> int:
    """This should be sync!"""
    # Simple calculation - should be sync
    return sum(numbers)  # No I/O, no need for async
```

### 🧪 Testing Strategies

#### **1. Testing Synchronous Functions**

```python
import pytest

def test_calculate_user_score():
    """Test synchronous user score calculation."""
    user_data = {
        'engagement': 80,
        'activity': 70,
        'quality': 90
    }
    
    score = calculate_user_score(user_data)
    
    assert score == 78.0  # (80*0.3) + (70*0.4) + (90*0.3)
    assert isinstance(score, float)

def test_validate_email_format():
    """Test email validation."""
    assert validate_email_format("user@example.com") is True
    assert validate_email_format("invalid-email") is False
    assert validate_email_format("") is False

def test_format_user_display_name():
    """Test name formatting."""
    result = format_user_display_name("john", "doe")
    assert result == "John Doe"
```

#### **2. Testing Asynchronous Functions**

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_fetch_user_from_database():
    """Test async user fetching."""
    # Mock database session
    with patch('your_module.get_database_session') as mock_session:
        mock_user = Mock()
        mock_user.to_dict.return_value = {"id": "123", "name": "John"}
        
        mock_session.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_user
        
        result = await fetch_user_from_database("123")
        
        assert result == {"id": "123", "name": "John"}

@pytest.mark.asyncio
async def test_call_external_api():
    """Test async API call."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success"}
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await call_external_api("https://api.example.com", {"data": "test"})
        
        assert result == {"status": "success"}
```

### 🔄 Migration Guide

#### **1. Converting Synchronous to Asynchronous**

```python
# Before: Synchronous function
def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """Fetch user data synchronously."""
    with get_database_session() as session:
        result = session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user.to_dict() if user else None

# After: Asynchronous function
async def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """Fetch user data asynchronously."""
    async with get_database_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user.to_dict() if user else None
```

#### **2. Converting Asynchronous to Synchronous**

```python
# Before: Unnecessary async function
async def calculate_simple_math(a: int, b: int) -> int:
    """Simple math calculation."""
    return a + b

# After: Synchronous function
def calculate_simple_math(a: int, b: int) -> int:
    """Simple math calculation."""
    return a + b
```

### 🎯 Best Practices

#### **1. Function Naming Conventions**

```python
# Synchronous functions
def calculate_user_score(user_data: Dict[str, Any]) -> float:
    """Calculate user score synchronously."""
    pass

def validate_input_data(data: Dict[str, Any]) -> List[str]:
    """Validate input data synchronously."""
    pass

# Asynchronous functions
async def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """Fetch user data asynchronously."""
    pass

async def process_file_upload(file_path: str) -> Dict[str, Any]:
    """Process file upload asynchronously."""
    pass
```

#### **2. Error Handling**

```python
# Synchronous error handling
def process_data_sync(data: List[float]) -> float:
    """Process data synchronously with error handling."""
    try:
        if not data:
            raise ValueError("Data cannot be empty")
        return sum(data) / len(data)
    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}")
        raise

# Asynchronous error handling
async def process_data_async(data: List[float]) -> float:
    """Process data asynchronously with error handling."""
    try:
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Simulate async processing
        await asyncio.sleep(0.1)
        return sum(data) / len(data)
    except Exception as e:
        logger.error(f"Async data processing failed: {str(e)}")
        raise
```

#### **3. Performance Optimization**

```python
# Parallel async operations
async def fetch_user_comprehensive_data(user_id: str) -> Dict[str, Any]:
    """Fetch comprehensive user data in parallel."""
    # Execute multiple async operations in parallel
    user_data, activity_data, preferences_data = await asyncio.gather(
        fetch_user_from_database(user_id),
        fetch_user_activity(user_id),
        fetch_user_preferences(user_id)
    )
    
    return {
        "user": user_data,
        "activity": activity_data,
        "preferences": preferences_data
    }

# Sequential async operations when order matters
async def process_user_registration_sequential(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process user registration sequentially."""
    # Create user first
    user = await create_user_in_database(user_data)
    
    # Then send welcome email
    await send_welcome_email(user["email"])
    
    # Finally update analytics
    await update_registration_analytics()
    
    return user
```

### 📊 Performance Metrics

#### **Expected Improvements**

- **I/O Operations**: 10-100x faster with async
- **Concurrent Requests**: Better resource utilization
- **Response Times**: Reduced latency for I/O-bound operations
- **Scalability**: Better handling of concurrent users

#### **Monitoring**

```python
import time
import asyncio

def measure_sync_performance(func):
    """Decorator to measure synchronous function performance."""
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        logger.info(f"Sync function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def measure_async_performance(func):
    """Decorator to measure asynchronous function performance."""
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        
        logger.info(f"Async function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper
```

### 🎉 Conclusion

Proper use of `def` for synchronous operations and `async def` for asynchronous operations is crucial for building performant and scalable FastAPI applications. This guide provides:

- **Clear guidelines** for when to use each type
- **Practical examples** for common scenarios
- **Performance considerations** and optimization strategies
- **Testing approaches** for both sync and async functions
- **Migration strategies** for converting between types
- **Best practices** for naming, error handling, and performance

By following these principles, you can build applications that efficiently handle both CPU-bound and I/O-bound operations, providing better user experience and system performance. 