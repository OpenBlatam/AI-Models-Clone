"""
Database models for ads functionality.

Required libraries:
aioboto3==14.0.0
aiohttp==3.11.16
alembic==1.10.4
asyncpg==0.27.0
atlassian-python-api==3.41.16
beautifulsoup4==4.12.3
boto3==1.36.23
celery==5.5.1
chardet==5.2.0
dask==2023.8.1
ddtrace==2.6.5
discord.py==2.4.0
distributed==2023.8.1
fastapi==0.115.12
fastapi-users==14.0.1
fastapi-users-db-sqlalchemy==5.0.0
filelock==3.15.4
google-api-python-client==2.86.0
google-cloud-aiplatform==1.58.0
google-auth-httplib2==0.1.0
google-auth-oauthlib==1.0.0
httpcore==1.0.5
httpx[http2]==0.27.0
httpx-oauth==0.15.1
huggingface-hub==0.29.0
inflection==0.5.1
jira==3.5.1
jsonref==1.1.0
trafilatura==1.12.2
langchain==0.3.23
langchain-community==0.3.21
langchain-core==0.3.51
langchain-openai==0.2.9
langchain-text-splitters==0.3.8
langchainhub==0.1.21
langgraph==0.2.72
langgraph-checkpoint==2.0.13
langgraph-sdk==0.1.44
litellm==1.69.0
lxml==5.3.0
lxml_html_clean==0.2.2
llama-index==0.12.28
Mako==1.2.4
msal==1.28.0
nltk==3.9.1
Office365-REST-Python-Client==2.5.9
oauthlib==3.2.2
openai==1.75.0
openpyxl==3.1.2
passlib==1.7.4
playwright==1.41.2
psutil==5.9.5
psycopg2-binary==2.9.9
puremagic==1.28
pyairtable==3.0.1
pycryptodome==3.19.1
pydantic==2.8.2
PyGithub==2.5.0
python-dateutil==2.8.2
python-gitlab==5.6.0
python-pptx==0.6.23
pypdf==5.4.0
pytest-mock==3.12.0
pytest-playwright==0.7.0
python-docx==1.1.2
python-dotenv==1.0.0
python-multipart==0.0.20
pywikibot==9.0.0
redis==5.0.8
requests==2.32.2
requests-oauthlib==1.3.1
retry==0.9.2
rfc3986==1.5.0
setfit==1.1.1
simple-salesforce==1.12.6
slack-sdk==3.20.2
SQLAlchemy[mypy]==2.0.15
starlette==0.46.1
supervisor==4.2.5
tiktoken==0.7.0
timeago==1.0.16
transformers==4.49.0
unstructured==0.15.1
unstructured-client==0.25.4
uvicorn==0.21.1
zulip==0.8.2
hubspot-api-client==8.1.0
asana==5.0.8
dropbox==11.36.2
boto3-stubs[s3]==1.34.133
shapely==2.0.6
stripe==10.12.0
urllib3==2.2.3
mistune==0.8.4
sentry-sdk==2.14.0
prometheus_client==0.21.0
fastapi-limiter==0.1.6
prometheus_fastapi_instrumentator==7.1.0
sendgrid==6.11.0
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from onyx.db.base import Base
from onyx.db.users import User

class AdsGeneration(Base):
    """Model for storing ads generation results."""
    __tablename__ = "ads_generations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String(255), nullable=True)
    type = Column(String(50), nullable=False)  # ads, brand-kit, custom
    prompt = Column(Text, nullable=True)
    content = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # Brand voice settings
    brand_voice = Column(JSON, nullable=True)  # Stores BrandVoice schema
    audience_profile = Column(JSON, nullable=True)  # Stores AudienceProfile schema
    project_context = Column(JSON, nullable=True)  # Stores ProjectContext schema

    # Relationships
    user = relationship("User", back_populates="ads_generations")
    analytics = relationship("AdsAnalytics", back_populates="ads_generation")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "url": self.url,
            "type": self.type,
            "prompt": self.prompt,
            "content": self.content,
            "metadata": self.metadata,
            "brand_voice": self.brand_voice,
            "audience_profile": self.audience_profile,
            "project_context": self.project_context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class BackgroundRemoval(Base):
    """Model for storing background removal results."""
    __tablename__ = "background_removals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_image_url = Column(String(255), nullable=True)
    processed_image_url = Column(String(255), nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # Image processing settings
    image_settings = Column(JSON, nullable=True)  # Stores image processing settings
    content_sources = Column(JSON, nullable=True)  # Stores ContentSource schema

    # Relationships
    user = relationship("User", back_populates="background_removals")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "original_image_url": self.original_image_url,
            "processed_image_url": self.processed_image_url,
            "metadata": self.metadata,
            "image_settings": self.image_settings,
            "content_sources": self.content_sources,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class AdsAnalytics(Base):
    """Model for storing ads analytics data."""
    __tablename__ = "ads_analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ads_generation_id = Column(Integer, ForeignKey("ads_generations.id"), nullable=False)
    metrics = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Email sequence metrics
    email_metrics = Column(JSON, nullable=True)  # Stores EmailSequenceMetrics schema
    email_settings = Column(JSON, nullable=True)  # Stores EmailSequenceSettings schema

    # Relationships
    user = relationship("User", back_populates="ads_analytics")
    ads_generation = relationship("AdsGeneration", back_populates="analytics")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ads_generation_id": self.ads_generation_id,
            "metrics": self.metrics,
            "email_metrics": self.email_metrics,
            "email_settings": self.email_settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Add relationships to User model
User.ads_generations = relationship("AdsGeneration", back_populates="user")
User.background_removals = relationship("BackgroundRemoval", back_populates="user")
User.ads_analytics = relationship("AdsAnalytics", back_populates="user") 