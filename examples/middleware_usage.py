from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import structlog
from middleware.core import (
from middleware.security import (
from middleware.performance import (
    import uvicorn
from typing import Any, List, Dict, Optional
import logging
"""
Comprehensive example showing how to use all middleware together.
Demonstrates logging, metrics, exception handling, security, and performance monitoring.
"""



    setup_structured_logging, create_log_context, log_operation, LogLevel,
    create_metric_context, record_metric, MetricType,
    create_exception_context, handle_exception,
    with_logging, with_metrics, with_exception_handling,
    setup_middleware_stack, operation_context
)

    create_security_context, validate_jwt_token, hash_password, verify_password,
    require_authentication, require_permission, require_role, rate_limit,
    setup_security_middleware, generate_jwt_token, sanitize_input,
    validate_email, validate_password_strength
)

    CacheManager, DatabaseProfiler,
    with_caching, with_database_profiling, with_performance_monitoring,
    setup_performance_middleware, initialize_cache, cleanup_cache,
    get_performance_statistics, optimize_database_queries
)


# =============================================================================
# APPLICATION SETUP
# =============================================================================

# Initialize structured logging
logger = setup_structured_logging(
    log_level="INFO",
    log_format="json",
    include_timestamp=True
)

# Create FastAPI app
app = FastAPI(
    title="Middleware Example API",
    description="Demonstrates comprehensive middleware usage",
    version="1.0.0"
)

# Setup all middleware
setup_middleware_stack(app)
setup_security_middleware(app)
setup_performance_middleware(app)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class User:
    """User data model."""
    id: str
    email: str
    password_hash: str
    salt: str
    roles: List[str]
    permissions: List[str]
    created_at: float


@dataclass
class Product:
    """Product data model."""
    id: str
    name: str
    price: float
    category: str
    stock: int


# =============================================================================
# MOCK DATABASE
# =============================================================================

# Mock data storage
users_db: Dict[str, User] = {}
products_db: Dict[str, Product] = {}

# Initialize mock data
def initialize_mock_data():
    """Initialize mock database with sample data."""
    # Create test user
    password_data = hash_password("secure_password123")
    users_db["user1"] = User(
        id="user1",
        email="user@example.com",
        password_hash=password_data["hash"],
        salt=password_data["salt"],
        roles=["user", "admin"],
        permissions=["read:products", "write:products", "delete:products"],
        created_at=time.time()
    )
    
    # Create test products
    products_db["prod1"] = Product(
        id="prod1",
        name="Laptop",
        price=999.99,
        category="electronics",
        stock=10
    )
    products_db["prod2"] = Product(
        id="prod2",
        name="Smartphone",
        price=599.99,
        category="electronics",
        stock=25
    )


# =============================================================================
# AUTHENTICATION FUNCTIONS
# =============================================================================

@with_logging("authenticate_user", "auth")
@with_metrics("authenticate_user", "auth")
async def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user with email and password.
    
    Args:
        email: User email
        password: User password
    
    Returns:
        Authentication result with token
    """
    # Find user by email
    user = None
    for u in users_db.values():
        if u.email == email:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(password, user.password_hash, user.salt):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    token_payload = {
        "user_id": user.id,
        "email": user.email,
        "roles": user.roles,
        "permissions": user.permissions
    }
    
    token = generate_jwt_token(token_payload, "your-secret-key", expires_in=3600)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "roles": user.roles
    }


@with_logging("get_current_user", "auth")
async def get_current_user(request: Request) -> User:
    """Get current user from request."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    token = auth_header.split(" ")[1]
    try:
        payload = validate_jwt_token(token, "your-secret-key")
        user_id = payload.get("user_id")
        
        if user_id not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        return users_db[user_id]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


# =============================================================================
# PRODUCT FUNCTIONS
# =============================================================================

@with_logging("get_products", "products")
@with_metrics("get_products", "products")
@with_caching(ttl=300, key_prefix="products")
async def get_products(category: str = None) -> List[Product]:
    """
    Get products with optional category filter.
    
    Args:
        category: Optional category filter
    
    Returns:
        List of products
    """
    # Simulate database query delay
    await asyncio.sleep(0.1)
    
    products = list(products_db.values())
    
    if category:
        products = [p for p in products if p.category == category]
    
    return products


@with_logging("get_product", "products")
@with_metrics("get_product", "products")
@with_caching(ttl=600, key_prefix="product")
async def get_product(product_id: str) -> Product:
    """
    Get product by ID.
    
    Args:
        product_id: Product identifier
    
    Returns:
        Product data
    """
    # Simulate database query delay
    await asyncio.sleep(0.05)
    
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return products_db[product_id]


@with_logging("create_product", "products")
@with_metrics("create_product", "products")
@with_performance_monitoring("create_product", "products")
async def create_product(
    name: str,
    price: float,
    category: str,
    stock: int,
    current_user: User
) -> Product:
    """
    Create new product.
    
    Args:
        name: Product name
        price: Product price
        category: Product category
        stock: Stock quantity
        current_user: Current authenticated user
    
    Returns:
        Created product
    """
    # Validate input
    if not name or len(name) < 2:
        raise HTTPException(status_code=400, detail="Invalid product name")
    
    if price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price")
    
    if stock < 0:
        raise HTTPException(status_code=400, detail="Invalid stock quantity")
    
    # Sanitize input
    sanitized_name = sanitize_input(name)
    sanitized_category = sanitize_input(category)
    
    # Simulate database operation
    await asyncio.sleep(0.2)
    
    product_id = f"prod{len(products_db) + 1}"
    product = Product(
        id=product_id,
        name=sanitized_name,
        price=price,
        category=sanitized_category,
        stock=stock
    )
    
    products_db[product_id] = product
    
    # Log product creation
    context = create_log_context(
        request_id="system",
        user_id=current_user.id,
        operation="product_created",
        component="products"
    )
    log_operation(
        logger,
        context,
        f"Product '{sanitized_name}' created by user {current_user.id}",
        product_id=product_id,
        price=price,
        category=sanitized_category
    )
    
    return product


@with_logging("update_product", "products")
@with_metrics("update_product", "products")
async def update_product(
    product_id: str,
    updates: Dict[str, Any],
    current_user: User
) -> Product:
    """
    Update product.
    
    Args:
        product_id: Product identifier
        updates: Update data
        current_user: Current authenticated user
    
    Returns:
        Updated product
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = products_db[product_id]
    
    # Apply updates
    if "name" in updates:
        product.name = sanitize_input(updates["name"])
    if "price" in updates:
        if updates["price"] <= 0:
            raise HTTPException(status_code=400, detail="Invalid price")
        product.price = updates["price"]
    if "category" in updates:
        product.category = sanitize_input(updates["category"])
    if "stock" in updates:
        if updates["stock"] < 0:
            raise HTTPException(status_code=400, detail="Invalid stock quantity")
        product.stock = updates["stock"]
    
    # Simulate database operation
    await asyncio.sleep(0.15)
    
    return product


@with_logging("delete_product", "products")
@with_metrics("delete_product", "products")
async def delete_product(product_id: str, current_user: User) -> Dict[str, str]:
    """
    Delete product.
    
    Args:
        product_id: Product identifier
        current_user: Current authenticated user
    
    Returns:
        Deletion confirmation
    """
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_name = products_db[product_id].name
    del products_db[product_id]
    
    # Simulate database operation
    await asyncio.sleep(0.1)
    
    # Log deletion
    context = create_log_context(
        request_id="system",
        user_id=current_user.id,
        operation="product_deleted",
        component="products"
    )
    log_operation(
        logger,
        context,
        f"Product '{product_name}' deleted by user {current_user.id}",
        product_id=product_id
    )
    
    return {"message": f"Product '{product_name}' deleted successfully"}


# =============================================================================
# API ROUTES
# =============================================================================

@app.post("/auth/login")
@with_exception_handling()
async def login(request: Request) -> Dict[str, Any]:
    """Login endpoint."""
    body = await request.json()
    email = body.get("email")
    password = body.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    return await authenticate_user(email, password)


@app.get("/products")
@rate_limit(limit=100, window=60)
async def list_products(
    category: str = None,
    request: Request = None
) -> List[Dict[str, Any]]:
    """List all products with optional category filter."""
    products = await get_products(category)
    
    # Convert to dict for JSON serialization
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category": p.category,
            "stock": p.stock
        }
        for p in products
    ]


@app.get("/products/{product_id}")
@rate_limit(limit=200, window=60)
async def get_product_by_id(
    product_id: str,
    request: Request = None
) -> Dict[str, Any]:
    """Get product by ID."""
    product = await get_product(product_id)
    
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "stock": product.stock
    }


@app.post("/products")
@require_authentication()
@require_permission("write:products")
@rate_limit(limit=10, window=60)
async def create_product_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create new product."""
    body = await request.json()
    
    product = await create_product(
        name=body.get("name"),
        price=body.get("price"),
        category=body.get("category"),
        stock=body.get("stock"),
        current_user=current_user
    )
    
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "stock": product.stock
    }


@app.put("/products/{product_id}")
@require_authentication()
@require_permission("write:products")
@rate_limit(limit=20, window=60)
async def update_product_endpoint(
    product_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update product."""
    body = await request.json()
    
    product = await update_product(product_id, body, current_user)
    
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "stock": product.stock
    }


@app.delete("/products/{product_id}")
@require_authentication()
@require_permission("delete:products")
@rate_limit(limit=5, window=60)
async def delete_product_endpoint(
    product_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete product."""
    return await delete_product(product_id, current_user)


@app.get("/metrics")
@require_authentication()
@require_role(["admin"])
async def get_metrics() -> Dict[str, Any]:
    """Get application metrics."""
    return {
        "performance": get_performance_statistics(),
        "database_optimizations": optimize_database_queries(),
        "cache_stats": get_cache_statistics()
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": str(time.time())}


# =============================================================================
# STARTUP AND SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    # Initialize mock data
    initialize_mock_data()
    
    # Initialize cache
    await initialize_cache()
    
    # Log startup
    context = create_log_context(
        request_id="system",
        operation="application_startup",
        component="system"
    )
    log_operation(
        logger,
        context,
        "Application started successfully"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    # Cleanup cache
    await cleanup_cache()
    
    # Log shutdown
    context = create_log_context(
        request_id="system",
        operation="application_shutdown",
        component="system"
    )
    log_operation(
        logger,
        context,
        "Application shutdown completed"
    )


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

async def demonstrate_middleware_usage():
    """Demonstrate middleware usage with example operations."""
    
    # Example 1: Login
    print("=== Example 1: User Login ===")
    login_data = {
        "email": "user@example.com",
        "password": "secure_password123"
    }
    
    # This would be a POST request in real usage
    print(f"Login attempt for: {login_data['email']}")
    
    # Example 2: Get products (cached)
    print("\n=== Example 2: Get Products (Cached) ===")
    products = await get_products()
    print(f"Retrieved {len(products)} products")
    
    # Example 3: Get products again (should hit cache)
    print("\n=== Example 3: Get Products (Cache Hit) ===")
    products = await get_products()
    print(f"Retrieved {len(products)} products (from cache)")
    
    # Example 4: Performance monitoring
    print("\n=== Example 4: Performance Monitoring ===")
    async with operation_context("batch_operation", "example"):
        # Simulate some work
        await asyncio.sleep(0.5)
        print("Batch operation completed")
    
    # Example 5: Error handling
    print("\n=== Example 5: Error Handling ===")
    try:
        await get_product("nonexistent")
    except HTTPException as e:
        print(f"Expected error: {e.detail}")
    
    # Example 6: Security validation
    print("\n=== Example 6: Security Validation ===")
    test_password = "weak"
    validation_result = validate_password_strength(test_password)
    print(f"Password strength: {validation_result}")


if __name__ == "__main__":
    
    print("Starting FastAPI application with comprehensive middleware...")
    print("Access the API at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    
    # Run the demonstration
    asyncio.run(demonstrate_middleware_usage())
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000) 