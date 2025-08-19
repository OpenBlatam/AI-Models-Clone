from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import json
import re
import uuid
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal, Annotated
from typing_extensions import TypedDict
import asyncio
from pydantic import (
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import PydanticCustomError, core_schema
from pydantic.functional_validators import BeforeValidator, PlainValidator
from pydantic.functional_serializers import PlainSerializer
import pydantic
        import traceback
from typing import Any, List, Dict, Optional
import logging
"""
Pydantic v2 Advanced Implementation
==================================

This module demonstrates:
- Pydantic v2 core features and improvements
- Advanced validation and serialization
- Model configuration and customization
- Field types and constraints
- Custom validators and serializers
- Performance optimizations
- Integration with FastAPI
- Real-world use cases
"""


    BaseModel, Field, ConfigDict, field_validator, model_validator,
    field_serializer, model_serializer, computed_field, AliasChoices,
    ValidationError, ValidationInfo, GetJsonSchemaHandler
)


# ============================================================================
# Basic Pydantic v2 Models
# ============================================================================

class UserModel(BaseModel):
    """Basic user model demonstrating Pydantic v2 features"""
    
    # Model configuration using ConfigDict (new in v2)
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Strip whitespace from strings
        validate_assignment=True,   # Validate on assignment
        extra='forbid',            # Forbid extra fields
        frozen=False,              # Allow mutation
        populate_by_name=True,     # Allow population by field name
        json_encoders={            # Custom JSON encoders
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
    )
    
    # Basic fields with validation
    id: int = Field(..., gt=0, description="User ID must be positive")
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    age: Optional[int] = Field(None, ge=0, le=150)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Field with alias
    full_name: str = Field(..., alias='fullName', description="User's full name")
    
    # Field with multiple aliases
    user_type: str = Field(..., alias=AliasChoices('userType', 'type'), description="User type")
    
    # Computed field (new in v2)
    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field for display name"""
        return f"{self.full_name} ({self.username})"
    
    # Field validator (new syntax in v2)
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        """Validate email domain"""
        if not v.endswith(('.com', '.org', '.net', '.edu')):
            raise ValueError('Email must have a valid domain')
        return v.lower()
    
    # Model validator (new syntax in v2)
    @model_validator(mode='before')
    @classmethod
    def validate_model_before(cls, data: Any) -> bool:
        """Validate model before creation"""
        if isinstance(data, dict):
            # Ensure username is lowercase
            if 'username' in data:
                data['username'] = data['username'].lower()
        return data
    
    @model_validator(mode='after')
    def validate_model_after(self) -> 'UserModel':
        """Validate model after creation"""
        if self.age and self.age < 18 and self.is_active:
            raise ValueError('Minors cannot be active users')
        return self


# ============================================================================
# Advanced Field Types and Constraints
# ============================================================================

class ProductModel(BaseModel):
    """Product model with advanced field types and constraints"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    # UUID field
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    
    # String with pattern and examples
    sku: str = Field(
        ...,
        pattern=r'^[A-Z]{2}-\d{4}-[A-Z0-9]{6}$',
        examples=['PR-1234-ABC123', 'EL-5678-XYZ789'],
        description="Product SKU in format XX-XXXX-XXXXXX"
    )
    
    # Decimal with precision
    price: Decimal = Field(..., ge=Decimal('0.01'), max_digits=10, decimal_places=2)
    
    # List with constraints
    tags: List[str] = Field(default_factory=list, max_length=10)
    
    # Dict with constraints
    metadata: Dict[str, Any] = Field(default_factory=dict, max_length=50)
    
    # Union types
    category: Union[str, int] = Field(..., description="Category as string or ID")
    
    # Literal types
    status: Literal['active', 'inactive', 'draft'] = Field(default='draft')
    
    # Optional with default
    description: Optional[str] = Field(None, max_length=1000)
    
    # Date and time fields
    created_at: date = Field(default_factory=date.today)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Field with custom validation
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        """Validate price is reasonable"""
        if v > Decimal('999999.99'):
            raise ValueError('Price too high')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and normalize tags"""
        if len(v) > 10:
            raise ValueError('Too many tags')
        return [tag.strip().lower() for tag in v if tag.strip()]


# ============================================================================
# Custom Types and Validators
# ============================================================================

# Custom type with validation
class Email(str):
    """Custom email type with validation"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        """Define custom validation schema"""
        return core_schema.with_info_after_validator_function(
            cls._validate_email,
            handler(source_type),
            serialization=core_schema.str_serializer(),
        )
    
    @classmethod
    def _validate_email(cls, v: str, info: ValidationInfo) -> str:
        """Validate email format"""
        if not isinstance(v, str):
            raise PydanticCustomError('email_type', 'Email must be a string')
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise PydanticCustomError('email_format', 'Invalid email format')
        
        return v.lower()


# Custom validator function
def validate_phone_number(v: str) -> str:
    """Validate phone number format"""
    if not isinstance(v, str):
        raise ValueError('Phone number must be a string')
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', v)
    
    if len(digits_only) not in [10, 11]:
        raise ValueError('Phone number must have 10 or 11 digits')
    
    # Format as (XXX) XXX-XXXX
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    else:
        return f"+{digits_only[0]} ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"


# Custom serializer function
def serialize_datetime(v: datetime) -> str:
    """Serialize datetime to ISO format"""
    return v.strftime('%Y-%m-%d %H:%M:%S')


class ContactModel(BaseModel):
    """Contact model with custom types and validators"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    # Custom email type
    email: Email = Field(..., description="Contact email")
    
    # Field with custom validator
    phone: str = Field(..., description="Contact phone number")
    
    # Field with custom serializer
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Apply custom validator
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_number(v)
    
    # Apply custom serializer
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        return serialize_datetime(value)


# ============================================================================
# Nested Models and Relationships
# ============================================================================

class AddressModel(BaseModel):
    """Address model for nested usage"""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    street: str = Field(..., max_length=100)
    city: str = Field(..., max_length=50)
    state: str = Field(..., max_length=2, pattern=r'^[A-Z]{2}$')
    zip_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$')
    country: str = Field(default='USA', max_length=50)
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate US state code"""
        valid_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }
        if v.upper() not in valid_states:
            raise ValueError('Invalid US state code')
        return v.upper()


class OrderItemModel(BaseModel):
    """Order item model"""
    
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0, le=1000)
    unit_price: Decimal = Field(..., ge=Decimal('0.01'))
    
    @computed_field
    @property
    def total_price(self) -> Decimal:
        """Calculate total price for this item"""
        return self.unit_price * Decimal(str(self.quantity))


class OrderModel(BaseModel):
    """Order model with nested models"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    customer_id: uuid.UUID
    items: List[OrderItemModel] = Field(..., min_length=1, max_length=100)
    shipping_address: AddressModel
    billing_address: Optional[AddressModel] = None
    status: Literal['pending', 'processing', 'shipped', 'delivered', 'cancelled'] = Field(default='pending')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Computed fields
    @computed_field
    @property
    def total_items(self) -> int:
        """Total number of items in order"""
        return sum(item.quantity for item in self.items)
    
    @computed_field
    @property
    def total_amount(self) -> Decimal:
        """Total amount for the order"""
        return sum(item.total_price for item in self.items)
    
    # Model validators
    @model_validator(mode='after')
    def validate_order(self) -> 'OrderModel':
        """Validate order after creation"""
        if self.total_amount > Decimal('10000.00'):
            raise ValueError('Order total cannot exceed $10,000')
        
        if self.billing_address is None:
            self.billing_address = self.shipping_address
        
        return self
    
    # Field serializers
    @field_serializer('total_amount')
    def serialize_total_amount(self, value: Decimal) -> str:
        """Serialize total amount as currency string"""
        return f"${value:.2f}"
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime fields"""
        return value.isoformat()


# ============================================================================
# Enums and Discriminated Unions
# ============================================================================

class PaymentMethod(str, Enum):
    """Payment method enum"""
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    PAYPAL = 'paypal'
    BANK_TRANSFER = 'bank_transfer'
    CRYPTO = 'crypto'


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class CreditCardPayment(BaseModel):
    """Credit card payment model"""
    type: Literal['credit_card'] = 'credit_card'
    card_number: str = Field(..., pattern=r'^\d{4}-\d{4}-\d{4}-\d{4}$')
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2024, le=2030)
    cvv: str = Field(..., pattern=r'^\d{3,4}$')
    
    @field_validator('card_number')
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Validate credit card number using Luhn algorithm"""
        digits = [int(d) for d in v.replace('-', '')]
        if len(digits) != 16:
            raise ValueError('Card number must have 16 digits')
        
        # Luhn algorithm
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled if doubled < 10 else doubled - 9
            else:
                checksum += digit
        
        if checksum % 10 != 0:
            raise ValueError('Invalid card number')
        
        return v


class PayPalPayment(BaseModel):
    """PayPal payment model"""
    type: Literal['paypal'] = 'paypal'
    email: Email
    transaction_id: Optional[str] = None


class PaymentModel(BaseModel):
    """Payment model with discriminated union"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    order_id: uuid.UUID
    amount: Decimal = Field(..., ge=Decimal('0.01'))
    method: Union[CreditCardPayment, PayPalPayment] = Field(..., discriminator='type')
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate payment amount"""
        if v > Decimal('50000.00'):
            raise ValueError('Payment amount cannot exceed $50,000')
        return v


# ============================================================================
# Performance Optimizations
# ============================================================================

class OptimizedModel(BaseModel):
    """Model optimized for performance"""
    
    # Use ConfigDict for better performance
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=False,  # Disable validation on assignment for performance
        extra='ignore',            # Ignore extra fields
        frozen=True,               # Make model immutable for better performance
        use_enum_values=True,      # Use enum values instead of enum objects
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }
    )
    
    # Use simple types for better performance
    id: int
    name: str
    value: float
    active: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Custom JSON Schema Generation
# ============================================================================

class CustomSchemaModel(BaseModel):
    """Model with custom JSON schema generation"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @classmethod
    def model_json_schema(
        cls,
        by_alias: bool = True,
        ref_template: str = '#/$defs/{model}',
        schema_generator: type[GetJsonSchemaHandler] = GetJsonSchemaHandler,
        mode: str = 'validation'
    ) -> JsonSchemaValue:
        """Generate custom JSON schema"""
        schema = super().model_json_schema(
            by_alias=by_alias,
            ref_template=ref_template,
            schema_generator=schema_generator,
            mode=mode
        )
        
        # Add custom properties to schema
        schema['title'] = 'Custom Schema Model'
        schema['description'] = 'A model with custom JSON schema generation'
        schema['examples'] = [
            {
                'id': 1,
                'name': 'Example Item',
                'metadata': {'key': 'value'}
            }
        ]
        
        return schema


# ============================================================================
# Async Validation
# ============================================================================

class AsyncValidationModel(BaseModel):
    """Model with async validation"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    username: str = Field(..., min_length=3, max_length=50)
    email: Email
    domain: str = Field(..., description="Domain to validate")
    
    @field_validator('domain')
    @classmethod
    async def validate_domain_exists(cls, v: str) -> str:
        """Async validation to check if domain exists"""
        # Simulate async domain validation
        await asyncio.sleep(0.1)
        
        # Simple domain validation (in real app, you'd check DNS)
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid domain format')
        
        return v.lower()


# ============================================================================
# TypedDict Support
# ============================================================================

class UserDict(TypedDict):
    """TypedDict for user data"""
    id: int
    username: str
    email: str
    is_active: bool


class TypedDictModel(BaseModel):
    """Model that works with TypedDict"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    user_data: UserDict
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('user_data')
    @classmethod
    def validate_user_data(cls, v: UserDict) -> UserDict:
        """Validate user data from TypedDict"""
        if not isinstance(v, dict):
            raise ValueError('User data must be a dictionary')
        
        required_fields = ['id', 'username', 'email', 'is_active']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Missing required field: {field}')
        
        return v


# ============================================================================
# Utility Functions
# ============================================================================

def create_user_model(data: Dict[str, Any]) -> UserModel:
    """Create user model with validation"""
    try:
        return UserModel(**data)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise


def validate_and_serialize(model: BaseModel) -> Dict[str, Any]:
    """Validate and serialize model to dict"""
    return model.model_dump(mode='json', exclude_none=True)


def create_model_from_json(json_str: str, model_class: type[BaseModel]) -> BaseModel:
    """Create model from JSON string"""
    data = json.loads(json_str)
    return model_class(**data)


def export_model_to_json(model: BaseModel, indent: int = 2) -> str:
    """Export model to JSON string"""
    return model.model_dump_json(indent=indent, exclude_none=True)


# ============================================================================
# Example Usage
# ============================================================================

def demonstrate_basic_usage():
    """Demonstrate basic Pydantic v2 usage"""
    print("\n=== Basic Usage Examples ===")
    
    # Create user model
    user_data = {
        'id': 1,
        'username': 'john_doe',
        'email': 'john@example.com',
        'age': 30,
        'fullName': 'John Doe',
        'userType': 'premium'
    }
    
    try:
        user = UserModel(**user_data)
        print(f"User created: {user.display_name}")
        print(f"User dict: {user.model_dump()}")
        print(f"User JSON: {user.model_dump_json()}")
    except ValidationError as e:
        print(f"Validation error: {e}")


def demonstrate_advanced_features():
    """Demonstrate advanced Pydantic v2 features"""
    print("\n=== Advanced Features Examples ===")
    
    # Product model
    product_data = {
        'sku': 'PR-1234-ABC123',
        'price': '29.99',
        'tags': ['electronics', 'gadgets'],
        'category': 'Electronics',
        'status': 'active',
        'description': 'A great product'
    }
    
    try:
        product = ProductModel(**product_data)
        print(f"Product created: {product.sku}")
        print(f"Product price: ${product.price}")
        print(f"Product tags: {product.tags}")
    except ValidationError as e:
        print(f"Validation error: {e}")


def demonstrate_nested_models():
    """Demonstrate nested models"""
    print("\n=== Nested Models Examples ===")
    
    # Order with nested models
    order_data = {
        'customer_id': str(uuid.uuid4()),
        'items': [
            {
                'product_id': str(uuid.uuid4()),
                'quantity': 2,
                'unit_price': '19.99'
            },
            {
                'product_id': str(uuid.uuid4()),
                'quantity': 1,
                'unit_price': '29.99'
            }
        ],
        'shipping_address': {
            'street': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            'zip_code': '10001'
        }
    }
    
    try:
        order = OrderModel(**order_data)
        print(f"Order created: {order.id}")
        print(f"Total items: {order.total_items}")
        print(f"Total amount: {order.total_amount}")
        print(f"Order JSON: {order.model_dump_json()}")
    except ValidationError as e:
        print(f"Validation error: {e}")


def demonstrate_payment_models():
    """Demonstrate payment models with discriminated unions"""
    print("\n=== Payment Models Examples ===")
    
    # Credit card payment
    credit_card_data = {
        'order_id': str(uuid.uuid4()),
        'amount': '99.99',
        'method': {
            'type': 'credit_card',
            'card_number': '1234-5678-9012-3456',
            'expiry_month': 12,
            'expiry_year': 2025,
            'cvv': '123'
        }
    }
    
    try:
        payment = PaymentModel(**credit_card_data)
        print(f"Payment created: {payment.id}")
        print(f"Payment method: {payment.method.type}")
        print(f"Payment amount: ${payment.amount}")
    except ValidationError as e:
        print(f"Validation error: {e}")


def demonstrate_performance_optimizations():
    """Demonstrate performance optimizations"""
    print("\n=== Performance Optimizations Examples ===")
    
    # Create optimized model
    optimized_data = {
        'id': 1,
        'name': 'Optimized Item',
        'value': 42.5,
        'active': True
    }
    
    try:
        optimized = OptimizedModel(**optimized_data)
        print(f"Optimized model created: {optimized.name}")
        print(f"Model is frozen: {optimized.model_config.get('frozen')}")
    except ValidationError as e:
        print(f"Validation error: {e}")


def demonstrate_custom_validation():
    """Demonstrate custom validation"""
    print("\n=== Custom Validation Examples ===")
    
    # Contact model with custom validation
    contact_data = {
        'email': 'contact@example.com',
        'phone': '5551234567'
    }
    
    try:
        contact = ContactModel(**contact_data)
        print(f"Contact created: {contact.email}")
        print(f"Formatted phone: {contact.phone}")
        print(f"Created at: {contact.created_at}")
    except ValidationError as e:
        print(f"Validation error: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling"""
    print("\n=== Error Handling Examples ===")
    
    # Invalid user data
    invalid_user_data = {
        'id': -1,  # Invalid: must be positive
        'username': 'a',  # Invalid: too short
        'email': 'invalid-email',  # Invalid: wrong format
        'fullName': 'Test User',
        'userType': 'invalid_type'  # Invalid: not in allowed values
    }
    
    try:
        user = UserModel(**invalid_user_data)
    except ValidationError as e:
        print("Validation errors:")
        for error in e.errors():
            print(f"  - {error['loc']}: {error['msg']}")


def demonstrate_serialization():
    """Demonstrate serialization features"""
    print("\n=== Serialization Examples ===")
    
    # Create model
    user = UserModel(
        id=1,
        username='test_user',
        email='test@example.com',
        fullName='Test User',
        userType='standard'
    )
    
    # Different serialization modes
    print(f"Model dict: {user.model_dump()}")
    print(f"Model dict (exclude unset): {user.model_dump(exclude_unset=True)}")
    print(f"Model dict (exclude defaults): {user.model_dump(exclude_defaults=True)}")
    print(f"Model JSON: {user.model_dump_json(indent=2)}")
    print(f"Model JSON (by alias): {user.model_dump_json(by_alias=True, indent=2)}")


def main():
    """Main function to demonstrate Pydantic v2 features"""
    print("Pydantic v2 Advanced Implementation Demonstrations")
    print("=" * 60)
    
    try:
        demonstrate_basic_usage()
        demonstrate_advanced_features()
        demonstrate_nested_models()
        demonstrate_payment_models()
        demonstrate_performance_optimizations()
        demonstrate_custom_validation()
        demonstrate_error_handling()
        demonstrate_serialization()
        
        print("\n" + "=" * 60)
        print("All Pydantic v2 Demonstrations Completed Successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during demonstrations: {str(e)}")
        traceback.print_exc()
        raise


match __name__:
    case "__main__":
    main() 