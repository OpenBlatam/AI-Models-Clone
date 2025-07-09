# 📧 Email Sequence Module - LangChain Integration

## 🎯 Overview

The Email Sequence Module is a comprehensive email automation system that integrates with LangChain to provide intelligent email sequence generation, personalization, and management. Built with Clean Architecture principles, it offers advanced features for creating, managing, and optimizing email campaigns.

## 🚀 Key Features

### 🤖 AI-Powered Features (LangChain Integration)
- **Intelligent Sequence Generation**: Create complete email sequences using AI
- **Smart Personalization**: Automatically personalize content based on subscriber data
- **Subject Line Optimization**: Generate compelling subject lines for better open rates
- **A/B Testing Variants**: Create multiple test variants using AI
- **Performance Analysis**: Get AI-powered insights and optimization suggestions

### 📊 Advanced Analytics
- **Real-time Tracking**: Monitor email performance in real-time
- **Engagement Metrics**: Track opens, clicks, conversions, and more
- **Subscriber Segmentation**: Advanced segmentation based on behavior and demographics
- **Performance Optimization**: AI-driven recommendations for improvement

### 🔧 Automation & Workflows
- **Multi-step Sequences**: Create complex email workflows
- **Conditional Logic**: Trigger emails based on subscriber behavior
- **Scheduled Delivery**: Intelligent timing and scheduling
- **Bulk Operations**: Efficient handling of large subscriber lists

### 🎨 Template Management
- **Dynamic Templates**: Variable-based templates with validation
- **Brand Consistency**: Maintain consistent branding across emails
- **Responsive Design**: Mobile-friendly email templates
- **Version Control**: Track template changes and versions

## 🏗️ Architecture

The module follows Clean Architecture principles with clear separation of concerns:

```
email_sequence/
├── 📦 models/           # Data models and entities
├── 🔧 services/         # Business logic and external integrations
├── ⚡ core/             # Core engine and orchestration
├── 🌐 api/              # API endpoints and schemas
├── 🛠️ utils/           # Utility functions and helpers
└── 🧪 tests/            # Test suite
```

### Core Components

1. **EmailSequenceEngine**: Main orchestrator for sequence management
2. **LangChainEmailService**: AI-powered email generation and personalization
3. **EmailDeliveryService**: Email sending and delivery management
4. **EmailAnalyticsService**: Analytics and performance tracking

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install langchain openai pydantic aiosmtplib

# Set up environment variables
export OPENAI_API_KEY="your-openai-api-key"
export SMTP_HOST="your-smtp-host"
export SMTP_USERNAME="your-smtp-username"
export SMTP_PASSWORD="your-smtp-password"
```

### Basic Usage

```python
import asyncio
from email_sequence import (
    EmailSequenceEngine,
    LangChainEmailService,
    EmailDeliveryService,
    EmailAnalyticsService,
    Subscriber
)

async def main():
    # Initialize services
    langchain_service = LangChainEmailService(
        api_key="your-openai-api-key",
        model_name="gpt-4"
    )
    
    delivery_service = EmailDeliveryService(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        smtp_username="your-email@gmail.com",
        smtp_password="your-password"
    )
    
    analytics_service = EmailAnalyticsService()
    
    # Initialize engine
    engine = EmailSequenceEngine(
        langchain_service=langchain_service,
        delivery_service=delivery_service,
        analytics_service=analytics_service
    )
    
    # Start engine
    await engine.start()
    
    # Create an AI-generated email sequence
    sequence = await engine.create_sequence(
        name="Welcome Series",
        target_audience="New subscribers interested in digital marketing",
        goals=["Onboarding", "Engagement", "Conversion"],
        tone="friendly",
        length=5
    )
    
    # Add subscribers
    subscribers = [
        Subscriber(
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            interests=["digital marketing", "automation"]
        )
    ]
    
    await engine.add_subscribers_to_sequence(sequence.id, subscribers)
    
    # Activate sequence
    await engine.activate_sequence(sequence.id)
    
    # Get analytics
    analytics = await engine.get_sequence_analytics(sequence.id)
    print(f"Sequence analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📧 Creating Email Sequences

### AI-Generated Sequences

```python
# Generate a complete sequence using AI
sequence = await langchain_service.generate_email_sequence(
    sequence_name="Product Launch",
    target_audience="Tech-savvy professionals aged 25-40",
    goals=["Awareness", "Interest", "Purchase"],
    tone="professional",
    length=7
)
```

### Manual Sequence Creation

```python
from email_sequence.models import EmailSequence, SequenceStep, StepType

# Create sequence manually
sequence = EmailSequence(
    name="Onboarding Series",
    description="Welcome new users to our platform"
)

# Add steps
welcome_step = SequenceStep(
    step_type=StepType.EMAIL,
    order=1,
    name="Welcome Email",
    subject="Welcome to our platform!",
    content="<h1>Welcome!</h1><p>We're excited to have you on board.</p>"
)

sequence.add_step(welcome_step)
```

## 🎨 Template Management

### Creating Templates

```python
from email_sequence.models import EmailTemplate, TemplateVariable, VariableType

# Create template with variables
template = EmailTemplate(
    name="Welcome Template",
    template_type="welcome",
    subject="Welcome {{first_name}}!",
    html_content="""
    <h1>Welcome {{first_name}}!</h1>
    <p>We're excited to have you join us.</p>
    <p>Your company: {{company}}</p>
    """
)

# Add variables
name_var = TemplateVariable(
    name="first_name",
    variable_type=VariableType.TEXT,
    required=True,
    description="Subscriber's first name"
)

template.add_variable(name_var)
```

### Personalizing Content

```python
# Personalize template for subscriber
personalized_content = await langchain_service.personalize_email_content(
    template=template,
    subscriber=subscriber,
    context={"campaign": "welcome_series"}
)

# Generate optimized subject line
subject_line = await langchain_service.generate_subject_line(
    email_content=personalized_content['html_content'],
    subscriber_data=subscriber.to_dict(),
    tone="friendly"
)
```

## 📊 Analytics & Performance

### Tracking Email Performance

```python
# Record email events
await analytics_service.record_email_sent(
    sequence_id=sequence.id,
    step_order=1,
    subscriber_id=subscriber.id
)

await analytics_service.record_email_opened(
    sequence_id=sequence.id,
    step_order=1,
    subscriber_id=subscriber.id
)

# Get performance insights
analysis = await langchain_service.analyze_email_performance(
    email_content=email_content,
    subject_line=subject_line,
    metrics={"open_rate": 25.5, "click_rate": 3.2}
)
```

### A/B Testing

```python
# Generate A/B test variants
variants = await langchain_service.generate_ab_test_variants(
    original_content="Get 20% off today!",
    test_type="subject",
    num_variants=3
)

# Test variants
for variant in variants:
    print(f"Variant: {variant['content']}")
```

## 🔧 Configuration

### Environment Variables

```bash
# LangChain Configuration
OPENAI_API_KEY=your-openai-api-key
LANGCHAIN_MODEL_NAME=gpt-4
LANGCHAIN_TEMPERATURE=0.7

# Email Delivery Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Analytics Configuration
ANALYTICS_ENABLED=true
ANALYTICS_DATABASE_URL=postgresql://user:pass@localhost/analytics
```

### Service Configuration

```python
# LangChain Service
langchain_service = LangChainEmailService(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("LANGCHAIN_MODEL_NAME", "gpt-4")
)

# Delivery Service
delivery_service = EmailDeliveryService(
    smtp_host=os.getenv("SMTP_HOST"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    smtp_username=os.getenv("SMTP_USERNAME"),
    smtp_password=os.getenv("SMTP_PASSWORD"),
    use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

### Example Test

```python
import pytest
from email_sequence.models import EmailSequence, Subscriber
from email_sequence.services import LangChainEmailService

@pytest.mark.asyncio
async def test_sequence_generation():
    service = LangChainEmailService(api_key="test-key")
    
    sequence = await service.generate_email_sequence(
        sequence_name="Test Sequence",
        target_audience="Test audience",
        goals=["Test goal"],
        length=3
    )
    
    assert sequence.name == "Test Sequence"
    assert len(sequence.steps) == 3
```

## 📈 Performance Optimization

### Best Practices

1. **Batch Processing**: Use bulk operations for large subscriber lists
2. **Caching**: Cache frequently accessed data
3. **Async Operations**: Use async/await for I/O operations
4. **Rate Limiting**: Respect API rate limits
5. **Error Handling**: Implement robust error handling

### Monitoring

```python
# Get delivery statistics
stats = delivery_service.get_delivery_statistics()
print(f"Success rate: {stats['success_rate']}%")

# Get sequence analytics
analytics = await engine.get_sequence_analytics(sequence_id)
print(f"Open rate: {analytics['open_rate']}%")
```

## 🔒 Security

### Data Protection

- **Encryption**: All sensitive data is encrypted
- **Authentication**: Secure API authentication
- **Rate Limiting**: Protection against abuse
- **Audit Logging**: Comprehensive activity logging

### Compliance

- **GDPR**: Full GDPR compliance support
- **CAN-SPAM**: CAN-SPAM Act compliance
- **Unsubscribe**: Automatic unsubscribe handling
- **Data Retention**: Configurable data retention policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- 📧 Email: support@example.com
- 📖 Documentation: [docs.example.com](https://docs.example.com)
- 🐛 Issues: [GitHub Issues](https://github.com/example/email-sequence/issues)

---

**Built with ❤️ using LangChain and Clean Architecture** 