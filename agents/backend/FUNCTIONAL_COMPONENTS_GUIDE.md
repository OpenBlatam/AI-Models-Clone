# Functional Components with Pydantic Models
## Complete Guide for FastAPI Applications

### 📋 Overview

This guide demonstrates how to implement **pure functional components** with **Pydantic v2 models** for input validation and response schemas in FastAPI applications. This approach provides:

- **Type Safety**: Full type checking with Pydantic models
- **Performance**: Optimized validation and serialization
- **Maintainability**: Pure functions are easier to test and reason about
- **Composability**: Components can be easily combined into pipelines
- **Monitoring**: Built-in performance metrics and error tracking
- **Caching**: Automatic result caching for expensive operations

### 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Functional     │    │   Pydantic      │
│   Endpoint      │───▶│   Component      │───▶│   Models        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Response      │    │   Performance    │    │   Validation    │
│   Schema        │    │   Monitoring     │    │   & Error       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🚀 Core Concepts

#### **1. Pure Functional Components**

Functional components are **pure functions** that:
- Take Pydantic models as input
- Return Pydantic models as output
- Have no side effects (except logging/monitoring)
- Are easily testable and composable

```python
@component(name="validate_user", cache_result=False)
def validate_user(input_data: UserInputModel) -> UserOutputModel:
    """Pure function for user validation."""
    # Validation logic here
    return UserOutputModel(...)
```

#### **2. Pydantic v2 Models**

Using Pydantic v2 for:
- **Input Validation**: Automatic validation of incoming data
- **Response Schemas**: Structured output with type safety
- **Performance**: Optimized with ORJSON integration
- **Documentation**: Auto-generated API docs

```python
class UserInputModel(BaseInputModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: Optional[int] = Field(None, ge=0, le=150)
```

#### **3. Component Composition**

Components can be composed into pipelines:

```python
# Sequential composition
user_pipeline = compose_components(
    validate_user,
    enrich_user_data,
    process_user_async
)

# Parallel execution
results = await execute_parallel([
    validate_user,
    check_user_permissions,
    load_user_preferences
], input_data)
```

### 📦 Installation and Setup

#### **1. Import Required Modules**

```python
from onyx.server.features.core.functional_components import (
    BaseInputModel, BaseOutputModel, ErrorOutputModel,
    component, async_component, compose_components,
    execute_parallel, conditional_component, retry_component
)
```

#### **2. Create Base Models**

```python
from pydantic import BaseModel, Field, computed_field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any

class BaseInputModel(OptimizedBaseModel):
    """Base input model with common fields."""
    request_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseOutputModel(OptimizedBaseModel):
    """Base output model with common fields."""
    success: bool = Field(..., description="Operation success status")
    data: Optional[Any] = Field(None, description="Result data")
    error: Optional[str] = Field(None, description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = Field(None, description="Execution time")
```

### 🎯 Creating Functional Components

#### **1. Basic Component**

```python
@component(name="validate_blog_post", cache_result=False)
def validate_blog_post(input_data: BlogPostInputModel) -> BlogPostOutputModel:
    """Validate blog post input data."""
    try:
        # Validation logic
        if len(input_data.content.split()) < 10:
            raise ValueError("Blog post must have at least 10 words")
        
        # Create output
        return BlogPostOutputModel(
            success=True,
            post_id=str(uuid.uuid4()),
            title=input_data.title,
            content=input_data.content,
            author_id=input_data.author_id,
            word_count=len(input_data.content.split())
        )
    except Exception as e:
        return ErrorOutputModel(
            success=False,
            error_code="VALIDATION_ERROR",
            error=str(e)
        )
```

#### **2. Async Component**

```python
@async_component(name="process_blog_post_async", cache_result=True, cache_ttl=300)
async def process_blog_post_async(input_data: BlogPostOutputModel) -> BlogPostOutputModel:
    """Async blog post processing."""
    try:
        # Simulate async processing
        await asyncio.sleep(0.1)
        
        # Add processing metadata
        processed_data = input_data.model_copy()
        processed_data.metadata.update({
            "processed": True,
            "processing_timestamp": datetime.utcnow().isoformat()
        })
        
        return processed_data
    except Exception as e:
        return ErrorOutputModel(
            success=False,
            error_code="ASYNC_PROCESSING_ERROR",
            error=str(e)
        )
```

#### **3. Component with Caching**

```python
@component(name="enrich_blog_post", cache_result=True, cache_ttl=600)
def enrich_blog_post(input_data: BlogPostOutputModel) -> BlogPostOutputModel:
    """Enrich blog post with metadata (cached for 10 minutes)."""
    try:
        enriched_data = input_data.model_copy()
        
        # Add SEO metadata
        enriched_data.metadata.update({
            "seo_title": f"{input_data.title} - Blog Post",
            "seo_description": input_data.excerpt,
            "keywords": input_data.tags,
            "enriched": True
        })
        
        return enriched_data
    except Exception as e:
        return ErrorOutputModel(
            success=False,
            error_code="ENRICHMENT_ERROR",
            error=str(e)
        )
```

### 🔧 Component Decorators

#### **1. @component Decorator**

```python
@component(
    name="my_component",           # Component name for metrics
    cache_result=True,             # Enable result caching
    cache_ttl=300,                 # Cache TTL in seconds
    validate_input=True,           # Validate input model
    validate_output=True,          # Validate output model
    log_execution=True             # Log execution details
)
def my_component(input_data: InputModel) -> OutputModel:
    # Component logic here
    pass
```

#### **2. @async_component Decorator**

```python
@async_component(
    name="my_async_component",
    cache_result=True,
    cache_ttl=300,
    validate_input=True,
    validate_output=True,
    log_execution=True
)
async def my_async_component(input_data: InputModel) -> OutputModel:
    # Async component logic here
    pass
```

### 🔄 Component Composition

#### **1. Sequential Composition**

```python
# Create a pipeline of components
blog_post_pipeline = compose_components(
    validate_blog_post,
    enrich_blog_post,
    process_blog_post_async
)

# Use the pipeline
result = blog_post_pipeline(input_data)
```

#### **2. Async Composition**

```python
# Create an async pipeline
async_blog_post_pipeline = compose_async_components(
    validate_blog_post,
    async_blog_post_processing,
    enrich_blog_post
)

# Use the async pipeline
result = await async_blog_post_pipeline(input_data)
```

#### **3. Parallel Execution**

```python
# Execute multiple components in parallel
results = await execute_parallel([
    validate_blog_post,
    check_author_permissions,
    load_blog_categories
], input_data)

# Process results
validation_result = results[0]
permissions_result = results[1]
categories_result = results[2]
```

#### **4. Conditional Execution**

```python
def is_premium_user(input_data: UserInputModel) -> bool:
    """Check if user is premium."""
    return input_data.metadata.get("premium", False)

# Conditional component
premium_user_processing = conditional_component(
    condition=is_premium_user,
    true_component=enrich_user_data,
    false_component=lambda x: x  # No enrichment for non-premium users
)

# Use conditional component
result = premium_user_processing(input_data)
```

#### **5. Retry Logic**

```python
# Add retry logic to a component
robust_processing = retry_component(
    component_func=async_blog_post_processing,
    max_retries=3,
    retry_delay=1.0,
    backoff_factor=2.0,
    retry_on_errors=[ConnectionError, TimeoutError]
)

# Use robust component
result = await robust_processing(input_data)
```

### 📊 FastAPI Integration

#### **1. Basic Endpoint**

```python
from fastapi import APIRouter, HTTPException, status
from .functional_components import BlogPostInputModel, BlogPostOutputModel

router = APIRouter(prefix="/blog", tags=["blog"])

@router.post("/posts", response_model=BlogPostOutputModel)
async def create_blog_post(input_data: BlogPostInputModel) -> BlogPostOutputModel:
    """Create a blog post using functional components."""
    try:
        # Process through pipeline
        result = blog_post_pipeline(input_data)
        
        # Check for errors
        if isinstance(result, ErrorOutputModel):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

#### **2. Async Endpoint with Background Tasks**

```python
from fastapi import BackgroundTasks

@router.post("/posts/async", response_model=BlogPostOutputModel)
async def create_blog_post_async(
    input_data: BlogPostInputModel,
    background_tasks: BackgroundTasks
) -> BlogPostOutputModel:
    """Create blog post with background processing."""
    try:
        # Immediate processing
        result = validate_blog_post(input_data)
        
        if isinstance(result, ErrorOutputModel):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
        
        # Add background task for async processing
        background_tasks.add_task(
            async_blog_post_processing,
            result
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

#### **3. Search Endpoint with Caching**

```python
@router.post("/search", response_model=SearchOutputModel)
async def search_posts(input_data: SearchInputModel) -> SearchOutputModel:
    """Search posts with caching."""
    try:
        # Execute search component (cached)
        result = search_blog_posts(input_data)
        
        if isinstance(result, ErrorOutputModel):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### 📈 Performance Monitoring

#### **1. Component Metrics**

```python
from .functional_components import get_component_metrics, get_all_metrics

# Get metrics for specific component
metrics = get_component_metrics("validate_blog_post")
print(f"Execution count: {metrics.execution_count}")
print(f"Average time: {metrics.average_execution_time:.3f}s")
print(f"Error rate: {metrics.error_rate:.2%}")

# Get all metrics
all_metrics = get_all_metrics()
for name, metric in all_metrics.items():
    print(f"{name}: {metric.execution_count} executions")
```

#### **2. Metrics Endpoint**

```python
@router.get("/metrics")
async def get_component_metrics() -> Dict[str, Any]:
    """Get performance metrics for all components."""
    metrics = get_all_metrics()
    
    serializable_metrics = {}
    for name, metric in metrics.items():
        serializable_metrics[name] = {
            "execution_count": metric.execution_count,
            "average_execution_time": metric.average_execution_time,
            "error_rate": metric.error_rate,
            "cache_hit_rate": metric.cache_hit_rate
        }
    
    return {
        "component_metrics": serializable_metrics,
        "total_components": len(metrics),
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 🧪 Testing Functional Components

#### **1. Unit Testing**

```python
import pytest
from .functional_components import validate_blog_post, BlogPostInputModel

def test_validate_blog_post_success():
    """Test successful blog post validation."""
    input_data = BlogPostInputModel(
        title="Test Post",
        content="This is a test blog post with enough content.",
        author_id="user123"
    )
    
    result = validate_blog_post(input_data)
    
    assert result.success is True
    assert result.title == "Test Post"
    assert result.word_count > 0

def test_validate_blog_post_short_content():
    """Test validation failure for short content."""
    input_data = BlogPostInputModel(
        title="Test Post",
        content="Short",  # Too short
        author_id="user123"
    )
    
    result = validate_blog_post(input_data)
    
    assert result.success is False
    assert "at least 10 words" in result.error
```

#### **2. Integration Testing**

```python
import pytest
from fastapi.testclient import TestClient
from .functional_endpoints import router

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

def test_create_blog_post_endpoint(client):
    """Test blog post creation endpoint."""
    response = client.post("/functional/blog-posts", json={
        "title": "Test Post",
        "content": "This is a test blog post with enough content.",
        "author_id": "user123",
        "tags": ["test", "blog"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["title"] == "Test Post"
```

### 🔒 Error Handling

#### **1. Component Error Handling**

```python
@component(name="safe_processing")
def safe_processing(input_data: InputModel) -> OutputModel:
    """Component with comprehensive error handling."""
    try:
        # Main processing logic
        result = process_data(input_data)
        
        # Validate result
        if not result.is_valid():
            raise ValueError("Invalid result")
        
        return OutputModel(success=True, data=result)
        
    except ValueError as e:
        # Handle validation errors
        return ErrorOutputModel(
            success=False,
            error_code="VALIDATION_ERROR",
            error=str(e),
            error_details={"type": "validation"}
        )
    except ConnectionError as e:
        # Handle connection errors
        return ErrorOutputModel(
            success=False,
            error_code="CONNECTION_ERROR",
            error=str(e),
            error_details={"type": "connection"}
        )
    except Exception as e:
        # Handle unexpected errors
        return ErrorOutputModel(
            success=False,
            error_code="UNEXPECTED_ERROR",
            error=str(e),
            error_details={"type": "unexpected"}
        )
```

#### **2. Endpoint Error Handling**

```python
@router.post("/posts", response_model=BlogPostOutputModel)
async def create_blog_post(input_data: BlogPostInputModel) -> BlogPostOutputModel:
    """Create blog post with error handling."""
    try:
        # Process through pipeline
        result = blog_post_pipeline(input_data)
        
        # Check for component errors
        if isinstance(result, ErrorOutputModel):
            # Map error codes to HTTP status codes
            status_code_map = {
                "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
                "AUTHORIZATION_ERROR": status.HTTP_401_UNAUTHORIZED,
                "PERMISSION_ERROR": status.HTTP_403_FORBIDDEN,
                "NOT_FOUND_ERROR": status.HTTP_404_NOT_FOUND,
                "RATE_LIMIT_ERROR": status.HTTP_429_TOO_MANY_REQUESTS,
            }
            
            http_status = status_code_map.get(
                result.error_code, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            raise HTTPException(
                status_code=http_status,
                detail={
                    "error": result.error,
                    "error_code": result.error_code,
                    "error_details": result.error_details
                }
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in blog post creation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### 🚀 Best Practices

#### **1. Model Design**

```python
# ✅ Good: Clear, focused models
class UserInputModel(BaseInputModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    age: Optional[int] = Field(None, ge=0, le=150)

# ❌ Bad: Overly complex models
class UserInputModel(BaseInputModel):
    name: str = Field(...)
    email: str = Field(...)
    age: Optional[int] = Field(None)
    # Too many fields in one model
    address: Dict[str, Any] = Field(...)
    preferences: Dict[str, Any] = Field(...)
    metadata: Dict[str, Any] = Field(...)
```

#### **2. Component Design**

```python
# ✅ Good: Single responsibility
@component(name="validate_user")
def validate_user(input_data: UserInputModel) -> UserOutputModel:
    """Validate user input data."""
    # Only validation logic here
    pass

@component(name="enrich_user")
def enrich_user(input_data: UserOutputModel) -> UserOutputModel:
    """Enrich user data with additional information."""
    # Only enrichment logic here
    pass

# ❌ Bad: Multiple responsibilities
@component(name="process_user")
def process_user(input_data: UserInputModel) -> UserOutputModel:
    """Validate, enrich, and process user data."""
    # Too many responsibilities in one component
    pass
```

#### **3. Error Handling**

```python
# ✅ Good: Specific error handling
@component(name="safe_processing")
def safe_processing(input_data: InputModel) -> OutputModel:
    try:
        return process_data(input_data)
    except ValidationError as e:
        return ErrorOutputModel(
            success=False,
            error_code="VALIDATION_ERROR",
            error=str(e)
        )
    except DatabaseError as e:
        return ErrorOutputModel(
            success=False,
            error_code="DATABASE_ERROR",
            error=str(e)
        )

# ❌ Bad: Generic error handling
@component(name="unsafe_processing")
def unsafe_processing(input_data: InputModel) -> OutputModel:
    try:
        return process_data(input_data)
    except Exception as e:
        return ErrorOutputModel(
            success=False,
            error_code="ERROR",
            error=str(e)
        )
```

#### **4. Performance Optimization**

```python
# ✅ Good: Use caching for expensive operations
@component(name="expensive_operation", cache_result=True, cache_ttl=300)
def expensive_operation(input_data: InputModel) -> OutputModel:
    # Expensive computation here
    pass

# ✅ Good: Use async for I/O operations
@async_component(name="async_operation")
async def async_operation(input_data: InputModel) -> OutputModel:
    # Async I/O operations here
    pass

# ✅ Good: Parallel execution for independent operations
results = await execute_parallel([
    operation1,
    operation2,
    operation3
], input_data)
```

### 📋 Complete Example

Here's a complete example showing how to implement a blog post system with functional components:

```python
# models.py
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import List, Optional

class BlogPostInputModel(BaseInputModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    author_id: str = Field(...)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(None)

class BlogPostOutputModel(BaseOutputModel):
    post_id: str = Field(...)
    title: str = Field(...)
    content: str = Field(...)
    author_id: str = Field(...)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(None)
    word_count: int = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @computed_field
    @property
    def excerpt(self) -> str:
        return self.content[:150] + "..." if len(self.content) > 150 else self.content

# components.py
@component(name="validate_blog_post")
def validate_blog_post(input_data: BlogPostInputModel) -> BlogPostOutputModel:
    """Validate blog post input."""
    try:
        word_count = len(input_data.content.split())
        
        return BlogPostOutputModel(
            success=True,
            post_id=str(uuid.uuid4()),
            title=input_data.title,
            content=input_data.content,
            author_id=input_data.author_id,
            tags=input_data.tags,
            category=input_data.category,
            word_count=word_count
        )
    except Exception as e:
        return ErrorOutputModel(
            success=False,
            error_code="VALIDATION_ERROR",
            error=str(e)
        )

@component(name="enrich_blog_post", cache_result=True, cache_ttl=300)
def enrich_blog_post(input_data: BlogPostOutputModel) -> BlogPostOutputModel:
    """Enrich blog post with metadata."""
    try:
        enriched_data = input_data.model_copy()
        enriched_data.metadata.update({
            "seo_title": f"{input_data.title} - Blog Post",
            "seo_description": input_data.excerpt,
            "keywords": input_data.tags,
            "enriched": True
        })
        return enriched_data
    except Exception as e:
        return ErrorOutputModel(
            success=False,
            error_code="ENRICHMENT_ERROR",
            error=str(e)
        )

# Pipeline
blog_post_pipeline = compose_components(
    validate_blog_post,
    enrich_blog_post
)

# endpoints.py
@router.post("/blog-posts", response_model=BlogPostOutputModel)
async def create_blog_post(input_data: BlogPostInputModel) -> BlogPostOutputModel:
    """Create a blog post using functional components."""
    try:
        result = blog_post_pipeline(input_data)
        
        if isinstance(result, ErrorOutputModel):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### 🎯 Benefits of This Approach

1. **Type Safety**: Full type checking with Pydantic models
2. **Performance**: Optimized validation and serialization
3. **Testability**: Pure functions are easy to test
4. **Composability**: Components can be easily combined
5. **Monitoring**: Built-in performance metrics
6. **Caching**: Automatic result caching
7. **Error Handling**: Structured error responses
8. **Documentation**: Auto-generated API docs
9. **Maintainability**: Clear separation of concerns
10. **Scalability**: Easy to add new components

This functional approach with Pydantic models provides a robust, maintainable, and performant foundation for building FastAPI applications. 