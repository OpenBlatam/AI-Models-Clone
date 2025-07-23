# Key Conventions

## Naming Conventions

### Variables and Functions
- Use descriptive names with auxiliary verbs for boolean variables
- Use lowercase with underscores for all names
- Be specific and avoid abbreviations

```python
# Boolean variables with auxiliary verbs
is_authenticated = True
has_valid_permissions = False
can_access_resource = True
should_retry_operation = False
needs_encryption = True
was_processed_successfully = True

# Descriptive function names
def validate_user_credentials(credentials: Dict[str, Any]) -> bool:
    return credentials.get('is_valid', False)

def has_required_permissions(user: User, resource: str) -> bool:
    return resource in user.permissions

def can_perform_action(user: User, action: str) -> bool:
    return action in user.allowed_actions

def should_apply_rate_limiting(user_id: str) -> bool:
    return get_user_request_count(user_id) > RATE_LIMIT_THRESHOLD

def needs_content_moderation(content: str) -> bool:
    return any(word in content.lower() for word in SENSITIVE_WORDS)

def was_operation_successful(result: Dict[str, Any]) -> bool:
    return result.get('status') == 'success'
```

### Files and Directories
- Use lowercase with underscores
- Be descriptive and indicate purpose
- Group related functionality

```
linkedin_posts/
├── api/
│   ├── posts_router.py
│   ├── users_router.py
│   └── analytics_router.py
├── services/
│   ├── post_service.py
│   ├── user_service.py
│   └── analytics_service.py
├── models/
│   ├── post_models.py
│   ├── user_models.py
│   └── response_models.py
├── utils/
│   ├── validation_utils.py
│   ├── formatting_utils.py
│   └── security_utils.py
├── config/
│   ├── database_config.py
│   ├── api_config.py
│   └── logging_config.py
└── tests/
    ├── test_post_service.py
    ├── test_user_service.py
    └── test_analytics_service.py
```

### Classes and Modules
- Use PascalCase for classes
- Use descriptive names that indicate purpose
- Group related functionality

```python
# Classes with descriptive names
class PostCreationService:
    def __init__(self, database_client: DatabaseClient):
        self.database_client = database_client

class UserAuthenticationHandler:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

class ContentModerationProcessor:
    def __init__(self, moderation_rules: List[str]):
        self.moderation_rules = moderation_rules

# Modules with clear purpose
# post_validation.py
def validate_post_content(content: str) -> bool:
    return len(content.strip()) > 0

# user_permissions.py
def check_user_permissions(user_id: str, action: str) -> bool:
    return has_permission(user_id, action)

# rate_limiting.py
def apply_rate_limiting(user_id: str) -> bool:
    return is_within_rate_limit(user_id)
```

### Constants and Configuration
- Use UPPER_CASE with underscores
- Group related constants
- Use descriptive names

```python
# API Configuration
API_BASE_URL = "https://api.linkedin.com/v2"
API_TIMEOUT_SECONDS = 30
API_RETRY_ATTEMPTS = 3

# Database Configuration
DATABASE_CONNECTION_POOL_SIZE = 20
DATABASE_QUERY_TIMEOUT = 10
DATABASE_MAX_RETRIES = 5

# Security Configuration
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 100
RATE_LIMIT_BURST_SIZE = 10
RATE_LIMIT_WINDOW_SECONDS = 60

# Content Validation
MAX_POST_LENGTH = 3000
MIN_POST_LENGTH = 10
ALLOWED_POST_TYPES = ["educational", "promotional", "personal"]
SENSITIVE_WORDS = ["spam", "inappropriate", "blocked"]
```

### Function Parameters and Return Values
- Use descriptive parameter names
- Indicate data types in names when helpful
- Use clear return value names

```python
def create_linkedin_post(
    post_content: str,
    user_id: str,
    access_token: str,
    should_publish_immediately: bool = True
) -> Dict[str, Any]:
    """Create a LinkedIn post with validation and publishing"""
    pass

def validate_user_permissions(
    user_id: str,
    required_permissions: List[str],
    resource_id: str = None
) -> bool:
    """Validate if user has required permissions"""
    pass

def process_post_analytics(
    post_id: str,
    analytics_data: Dict[str, Any],
    should_update_database: bool = True
) -> Dict[str, Any]:
    """Process and store post analytics"""
    pass

def check_rate_limit_status(
    user_id: str,
    current_timestamp: datetime,
    window_size_minutes: int = 1
) -> Dict[str, Any]:
    """Check current rate limit status for user"""
    pass
```

### Error Handling and Logging
- Use descriptive error message names
- Include context in error names
- Use consistent error naming patterns

```python
# Error types with descriptive names
class PostValidationError(Exception):
    """Raised when post validation fails"""
    pass

class UserAuthenticationError(Exception):
    """Raised when user authentication fails"""
    pass

class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded"""
    pass

class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass

# Logging with descriptive context
def log_post_creation_attempt(user_id: str, post_data: Dict[str, Any]):
    logger.info(f"User {user_id} attempting to create post", 
                extra={"user_id": user_id, "post_type": post_data.get("type")})

def log_authentication_failure(user_id: str, failure_reason: str):
    logger.warning(f"Authentication failed for user {user_id}: {failure_reason}",
                   extra={"user_id": user_id, "failure_reason": failure_reason})

def log_rate_limit_hit(user_id: str, current_requests: int, limit: int):
    logger.warning(f"Rate limit hit for user {user_id}: {current_requests}/{limit}",
                   extra={"user_id": user_id, "current_requests": current_requests, "limit": limit})
```

### Database and API Operations
- Use descriptive names for database operations
- Indicate operation type in function names
- Use clear parameter names

```python
# Database operations
async def create_post_in_database(post_data: Dict[str, Any]) -> str:
    """Create a new post in the database"""
    pass

async def retrieve_post_by_id(post_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a post by its ID"""
    pass

async def update_post_analytics(post_id: str, analytics: Dict[str, Any]) -> bool:
    """Update post analytics in database"""
    pass

async def delete_post_from_database(post_id: str) -> bool:
    """Delete a post from the database"""
    pass

# API operations
async def publish_post_to_linkedin(post_data: Dict[str, Any], access_token: str) -> Dict[str, Any]:
    """Publish post to LinkedIn API"""
    pass

async def fetch_user_profile_from_linkedin(user_id: str, access_token: str) -> Dict[str, Any]:
    """Fetch user profile from LinkedIn API"""
    pass

async def retrieve_post_analytics_from_linkedin(post_id: str, access_token: str) -> Dict[str, Any]:
    """Retrieve post analytics from LinkedIn API"""
    pass
```

### Configuration and Environment
- Use descriptive environment variable names
- Group related configuration
- Use clear default values

```python
# Environment variables
LINKEDIN_API_BASE_URL = os.getenv("LINKEDIN_API_BASE_URL", "https://api.linkedin.com/v2")
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/linkedin_posts")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Configuration classes
@dataclass
class DatabaseConfig:
    connection_url: str
    pool_size: int = 20
    max_retries: int = 3
    timeout_seconds: int = 30

@dataclass
class APIConfig:
    base_url: str
    timeout_seconds: int = 30
    max_retries: int = 3
    rate_limit_per_minute: int = 100

@dataclass
class SecurityConfig:
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
```

### Testing and Documentation
- Use descriptive test function names
- Include test scenario in names
- Use clear documentation strings

```python
# Test functions with descriptive names
def test_create_post_with_valid_data_should_succeed():
    """Test that creating a post with valid data succeeds"""
    pass

def test_create_post_with_invalid_content_should_fail():
    """Test that creating a post with invalid content fails"""
    pass

def test_user_without_permissions_cannot_create_post():
    """Test that users without permissions cannot create posts"""
    pass

def test_rate_limiting_prevents_excessive_requests():
    """Test that rate limiting prevents excessive API requests"""
    pass

# Documentation with clear descriptions
def validate_post_content(content: str) -> bool:
    """
    Validate post content meets requirements.
    
    Args:
        content: The post content to validate
        
    Returns:
        True if content is valid, False otherwise
        
    Raises:
        PostValidationError: If content validation fails
    """
    pass

def authenticate_user_credentials(username: str, password: str) -> bool:
    """
    Authenticate user credentials against the database.
    
    Args:
        username: The username to authenticate
        password: The password to verify
        
    Returns:
        True if credentials are valid, False otherwise
        
    Raises:
        UserAuthenticationError: If authentication process fails
    """
    pass
```

These conventions ensure code is readable, maintainable, and follows Python best practices while providing clear context about the purpose and behavior of each component. 