# Advanced FastAPI Implementation Summary

## Overview

This implementation provides a **comprehensive FastAPI application** that demonstrates advanced features, best practices, and real-world patterns for building scalable APIs. It includes authentication, database integration, background tasks, WebSockets, file uploads, and more.

## Key Features

### 1. Modern FastAPI Architecture
- **Async/await throughout** for high performance
- **Dependency injection** for clean code organization
- **Pydantic models** for data validation and serialization
- **OpenAPI documentation** with interactive Swagger UI

### 2. Authentication & Authorization
- **JWT token-based authentication** with access and refresh tokens
- **Password hashing** with bcrypt
- **Role-based access control** (user, superuser)
- **Token expiration** and automatic refresh

### 3. Database Integration
- **Async SQLAlchemy** with connection pooling
- **UUID primary keys** for security
- **Automatic timestamps** and soft deletes
- **Relationship management** between models

### 4. Advanced Features
- **Background tasks** for long-running operations
- **WebSocket support** for real-time communication
- **File upload** with validation and security
- **Rate limiting** and middleware
- **Streaming responses** for large datasets

## Implementation Components

### Application Structure

#### Main Application Setup
```python
def create_app() -> FastAPI:
    """Create FastAPI application"""
    # Create app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    
    # Add custom middleware
    app = RequestMiddleware(app)
    app = ResponseMiddleware(app)
    
    # Include routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(users_router, prefix=settings.API_V1_STR)
    app.include_router(projects_router, prefix=settings.API_V1_STR)
    app.include_router(models_router, prefix=settings.API_V1_STR)
    app.include_router(websocket_router, prefix=settings.API_V1_STR)
    
    # Add exception handlers
    app.add_exception_handler(HTTPException, FastAPIExceptionHandler.handle_http_exception)
    app.add_exception_handler(Exception, FastAPIExceptionHandler.handle_general_exception)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app
```

### Database Models

#### User Model
```python
class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[UUID4] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    full_name: Mapped[Optional[str]] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Project Model
```python
class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id: Mapped[UUID4] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    user_id: Mapped[UUID4] = mapped_column(sa.ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(default="active")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### ML Model Model
```python
class MLModel(Base):
    """ML Model model"""
    __tablename__ = "ml_models"
    
    id: Mapped[UUID4] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    model_type: Mapped[str] = mapped_column()
    version: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column()
    accuracy: Mapped[Optional[float]] = mapped_column()
    user_id: Mapped[UUID4] = mapped_column(sa.ForeignKey("users.id"))
    project_id: Mapped[Optional[UUID4]] = mapped_column(sa.ForeignKey("projects.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Pydantic Models

#### User Models
```python
class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, description="Password")
    
    @validator('password')
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserInDB(UserBase):
    """User in database model"""
    id: UUID4
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

#### Authentication Models
```python
class Token(BaseModel):
    """Token model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data model"""
    user_id: Optional[UUID4] = None
```

### Authentication System

#### Password Hashing
```python
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)
```

#### JWT Token Management
```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
```

#### Authentication Dependencies
```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: UUID4 = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### Database Integration

#### Database Setup
```python
# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### API Routes

#### Authentication Routes
```python
@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Register new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Send welcome notification
    background_tasks.add_task(send_notification_task, db_user.id, "Welcome to HeyGen AI!")
    
    return db_user


@auth_router.post("/login", response_model=Token)
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    # Get user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
```

#### Project Routes
```python
@projects_router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new project"""
    db_project = Project(
        **project.dict(),
        user_id=current_user.id
    )
    
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    return db_project


@projects_router.get("/", response_model=PaginatedResponse)
async def get_projects(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's projects"""
    offset = (pagination.page - 1) * pagination.size
    
    # Get total count
    result = await db.execute(
        select(func.count(Project.id))
        .where(Project.user_id == current_user.id)
    )
    total = result.scalar()
    
    # Get projects
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .offset(offset)
        .limit(pagination.size)
    )
    projects = result.scalars().all()
    
    pages = (total + pagination.size - 1) // pagination.size
    
    return PaginatedResponse(
        items=projects,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages
    )
```

#### ML Model Routes
```python
@models_router.post("/", response_model=MLModelResponse, status_code=status.HTTP_201_CREATED)
async def create_ml_model(
    model: MLModelCreate,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create new ML model"""
    # Validate file
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )
    
    # Save file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create model record
    db_model = MLModel(
        **model.dict(),
        file_path=str(file_path),
        user_id=current_user.id
    )
    
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)
    
    # Add background task to process model
    background_tasks.add_task(process_ml_model_task, db_model.id, db)
    
    return db_model
```

### Background Tasks

#### Task Implementation
```python
async def process_ml_model_task(model_id: UUID4, db: AsyncSession):
    """Background task to process ML model"""
    try:
        # Simulate ML model processing
        await asyncio.sleep(5)
        
        # Update model status
        await db.execute(
            update(MLModel)
            .where(MLModel.id == model_id)
            .values(accuracy=0.95)
        )
        await db.commit()
        
        logging.info(f"ML model {model_id} processed successfully")
    except Exception as e:
        logging.error(f"Error processing ML model {model_id}: {e}")


async def send_notification_task(user_id: UUID4, message: str):
    """Background task to send notification"""
    try:
        # Simulate notification sending
        await asyncio.sleep(2)
        logging.info(f"Notification sent to user {user_id}: {message}")
    except Exception as e:
        logging.error(f"Error sending notification to user {user_id}: {e}")
```

### WebSocket Support

#### Connection Manager
```python
class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Connect WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect WebSocket"""
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send personal message"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connections"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)


manager = ConnectionManager()


@websocket_router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo message back
            await manager.send_personal_message(f"Message text was: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Middleware

#### Custom Middleware
```python
class RequestMiddleware:
    """Custom request middleware"""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add request ID
            request_id = str(uuid.uuid4())
            scope["request_id"] = request_id
            
            # Add start time
            scope["start_time"] = time.time()
            
            # Log request
            logging.info(f"Request started: {request_id} - {scope['method']} {scope['path']}")
        
        await self.app(scope, receive, send)


class ResponseMiddleware:
    """Custom response middleware"""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = scope.get("request_id")
            start_time = scope.get("start_time")
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Add custom headers
                    headers = dict(message.get("headers", []))
                    headers[b"x-request-id"] = request_id.encode()
                    if start_time:
                        duration = time.time() - start_time
                        headers[b"x-response-time"] = f"{duration:.3f}".encode()
                    
                    message["headers"] = list(headers.items())
                
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
```

### Rate Limiting

#### Rate Limiter Implementation
```python
class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [req_time for req_time in self.requests[client_id] if req_time > minute_ago]
        else:
            self.requests[client_id] = []
        
        # Check rate limit
        if len(self.requests[client_id]) >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True


rate_limiter = RateLimiter()


async def check_rate_limit(request: Request):
    """Check rate limit for request"""
    client_id = request.client.host
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
```

## Usage Examples

### Basic API Usage
```python
# Start the server
# uvicorn fastapi_advanced_implementation:app --reload

# Access documentation
# http://localhost:8000/docs

# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "username": "testuser",
       "full_name": "Test User",
       "password": "SecurePass123"
     }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=user@example.com&password=SecurePass123"

# Create a project
curl -X POST "http://localhost:8000/api/v1/projects/" \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My ML Project",
       "description": "A machine learning project"
     }'

# Upload ML model
curl -X POST "http://localhost:8000/api/v1/models/" \
     -H "Authorization: Bearer <access_token>" \
     -F "model=@model.pkl" \
     -F "name=My Model" \
     -F "model_type=transformer" \
     -F "version=1.0.0"
```

### WebSocket Usage
```python
import websockets
import asyncio

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/ws/client123"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send("Hello, WebSocket!")
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")

# Run WebSocket test
asyncio.run(test_websocket())
```

### Background Tasks
```python
# Background tasks are automatically executed
# when creating users or uploading ML models

# Example: User registration with welcome notification
@auth_router.post("/register")
async def register(user: UserCreate, background_tasks: BackgroundTasks):
    # ... user creation logic ...
    
    # Add background task
    background_tasks.add_task(send_notification_task, user.id, "Welcome!")

# Example: ML model upload with processing
@models_router.post("/")
async def create_ml_model(model: MLModelCreate, background_tasks: BackgroundTasks):
    # ... model creation logic ...
    
    # Add background task
    background_tasks.add_task(process_ml_model_task, model.id)
```

## Benefits

### 1. Modern Architecture
- **Async/await throughout** for high performance
- **Type safety** with Pydantic models
- **Dependency injection** for clean code
- **OpenAPI documentation** with interactive UI

### 2. Security Features
- **JWT authentication** with token refresh
- **Password hashing** with bcrypt
- **Role-based access control**
- **Rate limiting** and input validation
- **CORS protection**

### 3. Database Integration
- **Async SQLAlchemy** with connection pooling
- **UUID primary keys** for security
- **Automatic timestamps** and relationships
- **Transaction management**

### 4. Advanced Features
- **Background tasks** for long-running operations
- **WebSocket support** for real-time communication
- **File upload** with validation
- **Streaming responses** for large datasets
- **Pagination** for large collections

### 5. Developer Experience
- **Interactive API documentation**
- **Comprehensive error handling**
- **Request/response logging**
- **Performance monitoring**
- **Testing support**

## Best Practices

### 1. Security
- **Use HTTPS** in production
- **Validate all inputs** with Pydantic
- **Hash passwords** with bcrypt
- **Implement rate limiting**
- **Use secure headers**

### 2. Performance
- **Use async/await** throughout
- **Implement connection pooling**
- **Add response compression**
- **Use background tasks** for heavy operations
- **Implement caching** where appropriate

### 3. Code Organization
- **Separate concerns** with routers
- **Use dependency injection**
- **Implement proper error handling**
- **Add comprehensive logging**
- **Write tests** for all endpoints

### 4. Database Design
- **Use UUIDs** for primary keys
- **Add indexes** for performance
- **Implement soft deletes**
- **Use foreign keys** for relationships
- **Add timestamps** for auditing

### 5. API Design
- **Follow REST conventions**
- **Use proper HTTP status codes**
- **Implement pagination**
- **Add filtering and sorting**
- **Provide comprehensive documentation**

## Conclusion

This advanced FastAPI implementation provides a comprehensive foundation for building scalable, secure, and performant APIs. It demonstrates modern Python web development practices and includes all the features needed for production applications.

Key benefits include:
- **Modern async architecture** for high performance
- **Comprehensive security** with JWT authentication
- **Robust database integration** with SQLAlchemy
- **Advanced features** like WebSockets and background tasks
- **Excellent developer experience** with interactive documentation
- **Production-ready** with proper error handling and monitoring

The implementation serves as a template for building real-world FastAPI applications and can be extended with additional features as needed. 