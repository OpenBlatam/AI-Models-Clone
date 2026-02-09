"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uuid

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.models import User, Organization, Document


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Set up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """Create a test client."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        is_active=True,
        is_verified=True,
        is_superuser=False
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    """Create a test superuser."""
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def test_organization(db_session: AsyncSession, test_user: User) -> Organization:
    """Create a test organization."""
    organization = Organization(
        id=uuid.uuid4(),
        name="Test Organization",
        slug="test-org",
        description="A test organization",
        subscription_plan="free",
        subscription_status="active",
        is_active=True,
        is_verified=True
    )
    
    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)
    
    return organization


@pytest.fixture
async def test_document(db_session: AsyncSession, test_user: User, test_organization: Organization) -> Document:
    """Create a test document."""
    document = Document(
        id=uuid.uuid4(),
        title="Test Document",
        description="A test document",
        content="This is test content",
        document_type="text",
        status="draft",
        organization_id=test_organization.id,
        owner_id=test_user.id,
        is_public=False,
        allow_comments=True,
        allow_editing=True,
        allow_sharing=True,
        view_count=0,
        edit_count=0,
        share_count=0
    )
    
    db_session.add(document)
    await db_session.commit()
    await db_session.refresh(document)
    
    return document


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user."""
    from app.core.auth import create_access_token
    
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def superuser_auth_headers(test_superuser: User) -> dict:
    """Create authentication headers for test superuser."""
    from app.core.auth import create_access_token
    
    access_token = create_access_token(data={"sub": str(test_superuser.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Generated content"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "total_tokens": 100,
            "prompt_tokens": 50,
            "completion_tokens": 50
        }
    }


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    return {
        "content": [
            {
                "text": "Generated content"
            }
        ],
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": 50,
            "output_tokens": 50
        }
    }


@pytest.fixture
def sample_ai_generation_request():
    """Sample AI generation request."""
    return {
        "prompt": "Write a short story about a robot",
        "provider": "openai",
        "model": "gpt-4",
        "max_tokens": 100,
        "temperature": 0.7
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "title": "Test Document",
        "description": "A test document",
        "content": "This is test content",
        "document_type": "text",
        "tags": ["test", "example"],
        "is_public": False,
        "allow_comments": True,
        "allow_editing": True,
        "allow_sharing": True
    }


@pytest.fixture
def sample_collaboration_data():
    """Sample collaboration data for testing."""
    return {
        "role": "editor",
        "permissions": {
            "can_edit": True,
            "can_comment": True,
            "can_share": False
        }
    }


@pytest.fixture
def sample_chat_message_data():
    """Sample chat message data for testing."""
    return {
        "content": "Hello everyone!",
        "message_type": "text",
        "metadata": {}
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add asyncio marker to async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # Add slow marker to tests that take longer
        if "slow" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.slow)




