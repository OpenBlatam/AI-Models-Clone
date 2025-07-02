"""
Enhanced Quality Demo
====================

Demonstración completa de las mejoras de calidad implementadas
con ejemplos prácticos de uso y características enterprise.
"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal

from enhanced_quality_config import get_enhanced_config
from enhanced_quality_schemas import (
    EnhancedProductCreateRequest,
    Money, Currency, SKU, Dimensions,
    ProductType, ProductStatus,
    ProductPricing, ProductInventory, ProductSEO,
    ProductIdentity
)
from enhanced_quality_services import (
    Result, EnhancedRedisCache, enhanced_services
)


async def demo_enhanced_quality_features():
    """Demostración completa de características enterprise."""
    
    print("\n🏗️ ENHANCED QUALITY API DEMO")
    print("=" * 50)
    
    # 1. CONFIGURACIÓN ENTERPRISE
    print("\n1. 📋 CONFIGURACIÓN ENTERPRISE")
    print("-" * 30)
    
    config = get_enhanced_config()
    print(f"✅ Environment: {config.environment.value}")
    print(f"✅ Version: {config.version}")
    print(f"✅ Debug Mode: {config.debug}")
    print(f"✅ AI Enabled: {config.ai_enabled}")
    print(f"✅ Production Ready: {config.is_production}")
    
    # Validación automática de configuración
    try:
        # Ejemplo de validación que fallaría en producción
        if config.is_production and config.debug:
            print("❌ Validation Error: Debug cannot be enabled in production")
        else:
            print("✅ Configuration validation passed")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    # 2. VALUE OBJECTS CON BUSINESS LOGIC
    print("\n2. 💰 VALUE OBJECTS CON BUSINESS LOGIC")
    print("-" * 40)
    
    # Money value object
    print("\n💰 Money Value Object:")
    price1 = Money(amount=Decimal("299.99"), currency=Currency.USD)
    price2 = Money(amount=Decimal("50.00"), currency=Currency.USD)
    
    total_price = price1 + price2
    discounted_price = price1 * 0.8
    
    print(f"   Base Price: {price1}")
    print(f"   Additional: {price2}")
    print(f"   Total: {total_price}")
    print(f"   80% Price: {discounted_price}")
    print(f"   Rounded: {discounted_price.round_to_currency()}")
    
    # SKU value object
    print("\n🏷️ SKU Generation:")
    auto_sku = SKU.generate(prefix="DEMO", category="ELECTRONICS")
    manual_sku = SKU(value="DEMO-MANUAL-001")
    
    print(f"   Auto-generated SKU: {auto_sku}")
    print(f"   Manual SKU: {manual_sku}")
    
    # Dimensions value object
    print("\n📦 Dimensions Calculations:")
    dimensions = Dimensions(length=30, width=20, height=10, weight=2.5)
    
    print(f"   Dimensions: {dimensions.length}x{dimensions.width}x{dimensions.height} cm")
    print(f"   Weight: {dimensions.weight} kg")
    print(f"   Volume: {dimensions.volume} cm³")
    print(f"   Is Oversized: {dimensions.is_oversized}")
    
    # 3. PRODUCT SCHEMAS CON VALIDACIONES AVANZADAS
    print("\n3. 📋 SCHEMAS CON VALIDACIONES AVANZADAS")
    print("-" * 45)
    
    try:
        # Crear producto con validaciones business rules
        product_request = EnhancedProductCreateRequest(
            name="Premium Wireless Headphones Pro",
            sku=auto_sku,
            description="Professional-grade wireless headphones with advanced noise cancellation technology and premium audio drivers.",
            short_description="Premium wireless headphones with noise cancellation",
            product_type=ProductType.PHYSICAL,
            
            # Pricing con business logic
            pricing=ProductPricing(
                base_price=Money(amount=Decimal("399.99"), currency=Currency.USD),
                cost_price=Money(amount=Decimal("200.00"), currency=Currency.USD),
                sale_price=Money(amount=Decimal("319.99"), currency=Currency.USD),
                tax_rate=0.10,
                maximum_discount_percent=25.0
            ),
            
            # Inventory con gestión inteligente
            inventory=ProductInventory(
                quantity=150,
                reserved_quantity=10,
                low_stock_threshold=20,
                reorder_point=50,
                reorder_quantity=100,
                dimensions=dimensions
            ),
            
            # SEO optimizado
            seo=ProductSEO(
                meta_title="Premium Wireless Headphones Pro - Professional Audio",
                meta_description="Experience professional-grade audio with our Premium Wireless Headphones Pro featuring advanced noise cancellation, premium drivers, and all-day comfort for audiophiles and professionals.",
                keywords=["wireless", "headphones", "professional", "audio", "noise-cancellation"],
                tags=["premium", "bluetooth", "audiophile", "professional"],
                og_title="Premium Wireless Headphones Pro",
                og_description="Professional-grade wireless headphones with advanced features"
            ),
            
            category_ids=["electronics", "audio", "headphones"],
            brand_id="premium-audio-co",
            attributes={
                "color_options": ["black", "silver", "white"],
                "connectivity": ["bluetooth-5.0", "3.5mm-jack", "usb-c"],
                "battery_life": "30 hours",
                "driver_size": "40mm",
                "frequency_response": "20Hz-20kHz"
            },
            image_urls=["https://example.com/headphones-main.jpg"]
        )
        
        print("✅ Product schema created successfully!")
        print(f"   Name: {product_request.name}")
        print(f"   SKU: {product_request.sku}")
        print(f"   Base Price: {product_request.pricing.base_price}")
        print(f"   Effective Price: {product_request.pricing.effective_price}")
        print(f"   Discount: {product_request.pricing.discount_percentage:.1f}%")
        print(f"   Profit Margin: {product_request.pricing.profit_margin:.1f}%")
        print(f"   Available Stock: {product_request.inventory.available_quantity}")
        print(f"   Is Low Stock: {product_request.inventory.is_low_stock}")
        print(f"   Needs Reorder: {product_request.inventory.needs_reorder}")
        
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
    
    # 4. ADVANCED ERROR HANDLING CON RESULT PATTERN
    print("\n4. 🛡️ ADVANCED ERROR HANDLING")
    print("-" * 35)
    
    # Simulación de operaciones con Result pattern
    def simulate_database_operation(success: bool) -> Result[dict]:
        """Simula operación de base de datos."""
        if success:
            return Result.ok({"id": "prod_123", "name": "Test Product"})
        else:
            from enhanced_quality_services import ValidationError
            return Result.fail(ValidationError("Database connection failed", code="DB_ERROR"))
    
    # Operación exitosa
    success_result = simulate_database_operation(True)
    if success_result.success:
        print(f"✅ Success: {success_result.value}")
    
    # Operación fallida
    fail_result = simulate_database_operation(False)
    if not fail_result.success:
        print(f"❌ Error: {fail_result.error.message} (Code: {fail_result.error.code})")
    
    # Unwrap seguro
    safe_value = fail_result.unwrap_or({"id": "default", "name": "Default Product"})
    print(f"🔄 Fallback value: {safe_value}")
    
    # 5. CACHE SERVICE CON CIRCUIT BREAKER
    print("\n5. ⚡ CACHE SERVICE ENTERPRISE")
    print("-" * 35)
    
    try:
        # Inicializar cache
        cache = EnhancedRedisCache(
            redis_url="redis://localhost:6379/1",  # Use test DB
            max_connections=10
        )
        
        init_result = await cache.initialize()
        if init_result.success:
            print("✅ Cache initialized successfully")
            
            # Test cache operations
            test_data = {
                "product_id": "test_123",
                "name": "Test Product",
                "price": 99.99,
                "timestamp": datetime.now().isoformat()
            }
            
            # Set value
            set_result = await cache.set("test:product:123", test_data, ttl=300)
            if set_result.success:
                print("✅ Cache set successful")
            
            # Get value
            get_result = await cache.get("test:product:123")
            if get_result.success and get_result.value:
                print(f"✅ Cache get successful: {get_result.value['name']}")
            
            # Batch operations
            batch_data = {
                "test:product:1": {"name": "Product 1"},
                "test:product:2": {"name": "Product 2"},
                "test:product:3": {"name": "Product 3"}
            }
            
            # Set multiple
            batch_set = await cache.set_many(batch_data, ttl=300)
            if batch_set.success:
                print("✅ Batch set successful")
            
            # Get multiple
            batch_get = await cache.get_many(list(batch_data.keys()))
            if batch_get.success:
                print(f"✅ Batch get successful: {len(batch_get.value)} items retrieved")
            
            # Health check
            health_result = await cache.health_check()
            if health_result.success:
                health_data = health_result.value
                print(f"✅ Cache health: {health_data['status']}")
                print(f"   Hit ratio: {health_data['hit_ratio']:.2%}")
                print(f"   Response time: {health_data['response_time_ms']:.1f}ms")
            
            # Cleanup
            await cache.close()
            
        else:
            print(f"❌ Cache initialization failed: {init_result.error}")
            
    except Exception as e:
        print(f"⚠️ Cache demo error (Redis not available): {e}")
    
    # 6. BUSINESS LOGIC AVANZADA
    print("\n6. 🏭 BUSINESS LOGIC AVANZADA")
    print("-" * 35)
    
    # Simulación de reglas de negocio
    def validate_pricing_business_rules(pricing: ProductPricing) -> Result[bool]:
        """Valida reglas de negocio de pricing."""
        try:
            # Regla 1: Margen mínimo de ganancia
            if pricing.profit_margin and pricing.profit_margin < 10:
                return Result.fail(ValidationError(
                    "Profit margin must be at least 10%",
                    code="INSUFFICIENT_MARGIN"
                ))
            
            # Regla 2: Descuento máximo
            if pricing.discount_percentage > 50:
                return Result.fail(ValidationError(
                    "Discount cannot exceed 50%",
                    code="EXCESSIVE_DISCOUNT"
                ))
            
            # Regla 3: Precio mínimo
            if pricing.effective_price.amount < Decimal("10.00"):
                return Result.fail(ValidationError(
                    "Product price cannot be below $10.00",
                    code="PRICE_TOO_LOW"
                ))
            
            return Result.ok(True)
            
        except Exception as e:
            return Result.fail(ValidationError(f"Business rule validation failed: {e}"))
    
    # Test business rules
    validation_result = validate_pricing_business_rules(product_request.pricing)
    if validation_result.success:
        print("✅ All business rules passed")
    else:
        print(f"❌ Business rule violation: {validation_result.error.message}")
    
    # 7. MONITORING Y MÉTRICAS
    print("\n7. 📊 MONITORING Y MÉTRICAS")
    print("-" * 35)
    
    # Simulación de métricas
    metrics_data = {
        "api_requests_total": 1543,
        "cache_hit_ratio": 0.87,
        "average_response_time_ms": 45.3,
        "error_rate": 0.002,
        "active_connections": 12,
        "products_created_today": 25,
        "revenue_today": 12450.75
    }
    
    print("📈 Current Metrics:")
    for metric, value in metrics_data.items():
        if isinstance(value, float):
            if metric.endswith('_ratio') or metric.startswith('error_'):
                print(f"   {metric}: {value:.2%}")
            else:
                print(f"   {metric}: {value:.2f}")
        else:
            print(f"   {metric}: {value:,}")
    
    # 8. RESUMEN DE CALIDAD
    print("\n8. 🎯 RESUMEN DE CALIDAD IMPLEMENTADA")
    print("-" * 45)
    
    quality_features = [
        "✅ Configuración enterprise con validaciones exhaustivas",
        "✅ Value objects con business logic integrada",
        "✅ Schemas con validaciones avanzadas y business rules",
        "✅ Result pattern para manejo robusto de errores",
        "✅ Cache service con circuit breaker y health checks",
        "✅ Business logic separada con patterns enterprise",
        "✅ Type safety completa con generics y protocols",
        "✅ Monitoring y métricas comprehensive",
        "✅ Production-ready patterns y resilience",
        "✅ Clean Architecture con separation of concerns"
    ]
    
    for feature in quality_features:
        print(f"   {feature}")
    
    print(f"\n🎉 ENHANCED QUALITY DEMO COMPLETED!")
    print("=" * 50)
    print("🏆 API elevada a estándares ENTERPRISE con:")
    print("   📋 15+ validaciones avanzadas por schema")
    print("   🛡️ Circuit breaker y error handling robusto")
    print("   ⚡ Performance optimizations y caching")
    print("   📊 Monitoring comprehensive y health checks")
    print("   🏗️ Clean Architecture con patterns avanzados")
    print("   🚀 Production-ready con resilience patterns")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_quality_features()) 