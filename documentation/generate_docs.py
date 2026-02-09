#!/usr/bin/env python3
"""
Documentation Generator for Instagram Captions API v10.0
Generates comprehensive API documentation in multiple formats.
"""
import sys
import os
from pathlib import Path
import logging
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from documentation.api_documentation import (
    APIDocumentation, APIEndpoint, APIModel
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_instagram_captions_api_docs() -> APIDocumentation:
    """Create comprehensive documentation for Instagram Captions API."""
    
    # Initialize API documentation
    api_docs = APIDocumentation(
        title="Instagram Captions API",
        version="10.0.0"
    )
    
    # Set API information
    api_docs.set_info(
        description="""A comprehensive API for generating, managing, and optimizing Instagram captions. 
        This API provides advanced caption generation, hashtag optimization, engagement analysis, 
        and multi-language support for Instagram content creators and marketers.""",
        contact={
            "name": "API Support",
            "email": "support@blatam-academy.com",
            "url": "https://blatam-academy.com"
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    )
    
    # Add servers
    api_docs.add_server("https://api.blatam-academy.com", "Production Server")
    api_docs.add_server("https://staging-api.blatam-academy.com", "Staging Server")
    api_docs.add_server("http://localhost:8000", "Local Development")
    
    # Add tags
    api_docs.add_tag("captions", "Caption generation and management")
    api_docs.add_tag("hashtags", "Hashtag optimization and analysis")
    api_docs.add_tag("engagement", "Engagement metrics and analysis")
    api_docs.add_tag("multilingual", "Multi-language support")
    api_docs.add_tag("analytics", "Analytics and reporting")
    api_docs.add_tag("templates", "Caption templates and presets")
    api_docs.add_tag("branding", "Brand voice and customization")
    api_docs.add_tag("compliance", "Content compliance and safety")
    
    # Add data models
    _add_data_models(api_docs)
    
    # Add API endpoints
    _add_api_endpoints(api_docs)
    
    return api_docs

def _add_data_models(api_docs: APIDocumentation):
    """Add data models to the API documentation."""
    
    # Caption Generation Request
    caption_request = APIModel(
        name="CaptionGenerationRequest",
        type="object",
        description="Request model for generating Instagram captions",
        properties={
            "content_type": {
                "type": "string",
                "description": "Type of content (post, story, reel, carousel)",
                "enum": ["post", "story", "reel", "carousel"]
            },
            "topic": {
                "type": "string",
                "description": "Main topic or theme of the content",
                "maxLength": 200
            },
            "tone": {
                "type": "string",
                "description": "Desired tone of the caption",
                "enum": ["casual", "professional", "humorous", "inspirational", "educational"]
            },
            "target_audience": {
                "type": "string",
                "description": "Target audience demographic",
                "maxLength": 100
            },
            "brand_voice": {
                "type": "string",
                "description": "Brand voice guidelines",
                "maxLength": 500
            },
            "hashtag_count": {
                "type": "integer",
                "description": "Number of hashtags to include",
                "minimum": 0,
                "maximum": 30
            },
            "language": {
                "type": "string",
                "description": "Language for the caption",
                "default": "en",
                "enum": ["en", "es", "fr", "de", "pt", "it"]
            },
            "include_emoji": {
                "type": "boolean",
                "description": "Whether to include emojis",
                "default": True
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum caption length",
                "minimum": 50,
                "maximum": 2200
            }
        },
        required=["content_type", "topic", "tone"],
        example={
            "content_type": "post",
            "topic": "Sustainable fashion tips",
            "tone": "educational",
            "target_audience": "eco-conscious millennials",
            "hashtag_count": 15,
            "language": "en",
            "include_emoji": True,
            "max_length": 500
        }
    )
    api_docs.add_model(caption_request)
    
    # Caption Response
    caption_response = APIModel(
        name="CaptionResponse",
        type="object",
        description="Response model for generated captions",
        properties={
            "caption_id": {
                "type": "string",
                "description": "Unique identifier for the generated caption"
            },
            "caption_text": {
                "type": "string",
                "description": "The generated caption text"
            },
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of optimized hashtags"
            },
            "engagement_score": {
                "type": "number",
                "description": "Predicted engagement score (0-100)"
            },
            "readability_score": {
                "type": "number",
                "description": "Readability score (0-100)"
            },
            "sentiment_score": {
                "type": "number",
                "description": "Sentiment analysis score (-1 to 1)"
            },
            "word_count": {
                "type": "integer",
                "description": "Number of words in the caption"
            },
            "character_count": {
                "type": "integer",
                "description": "Number of characters in the caption"
            },
            "generated_at": {
                "type": "string",
                "format": "date-time",
                "description": "Timestamp when caption was generated"
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata about the generation"
            }
        },
        required=["caption_id", "caption_text", "hashtags", "engagement_score"],
        example={
            "caption_id": "cap_12345",
            "caption_text": "🌱 Sustainable fashion isn't just a trend—it's a lifestyle choice that benefits our planet and future generations. Here are 5 simple ways to make your wardrobe more eco-friendly: 1️⃣ Choose quality over quantity 2️⃣ Support ethical brands 3️⃣ Embrace second-hand shopping 4️⃣ Care for your clothes properly 5️⃣ Recycle and upcycle What's your favorite sustainable fashion tip? Share below! 👗♻️",
            "hashtags": ["#SustainableFashion", "#EcoFriendly", "#SlowFashion", "#EthicalFashion", "#GreenLiving", "#FashionRevolution", "#ConsciousConsumer", "#EcoStyle", "#SustainableLiving", "#FashionForGood", "#GreenFashion", "#EcoConscious", "#SustainableStyle", "#FashionSustainability", "#EcoFashionista"],
            "engagement_score": 87.5,
            "readability_score": 92.3,
            "sentiment_score": 0.8,
            "word_count": 45,
            "character_count": 298,
            "generated_at": "2024-01-15T10:30:00Z"
        }
    )
    api_docs.add_model(caption_response)
    
    # Hashtag Analysis
    hashtag_analysis = APIModel(
        name="HashtagAnalysis",
        type="object",
        description="Analysis results for hashtag optimization",
        properties={
            "hashtag": {
                "type": "string",
                "description": "The hashtag text"
            },
            "popularity_score": {
                "type": "number",
                "description": "Popularity score (0-100)"
            },
            "competition_level": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Competition level for the hashtag"
            },
            "reach_potential": {
                "type": "number",
                "description": "Potential reach score (0-100)"
            },
            "trending": {
                "type": "boolean",
                "description": "Whether the hashtag is currently trending"
            },
            "related_hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Related hashtag suggestions"
            }
        },
        required=["hashtag", "popularity_score", "competition_level"],
        example={
            "hashtag": "#SustainableFashion",
            "popularity_score": 85.2,
            "competition_level": "high",
            "reach_potential": 78.9,
            "trending": True,
            "related_hashtags": ["#EcoFashion", "#SlowFashion", "#EthicalFashion"]
        }
    )
    api_docs.add_model(hashtag_analysis)
    
    # Engagement Metrics
    engagement_metrics = APIModel(
        name="EngagementMetrics",
        type="object",
        description="Engagement analysis metrics for captions",
        properties={
            "likes": {
                "type": "integer",
                "description": "Number of likes"
            },
            "comments": {
                "type": "integer",
                "description": "Number of comments"
            },
            "shares": {
                "type": "integer",
                "description": "Number of shares"
            },
            "saves": {
                "type": "integer",
                "description": "Number of saves"
            },
            "engagement_rate": {
                "type": "number",
                "description": "Overall engagement rate percentage"
            },
            "reach": {
                "type": "integer",
                "description": "Total reach count"
            },
            "impressions": {
                "type": "integer",
                "description": "Total impression count"
            }
        },
        required=["likes", "comments", "engagement_rate"],
        example={
            "likes": 1250,
            "comments": 89,
            "shares": 45,
            "saves": 156,
            "engagement_rate": 8.7,
            "reach": 15420,
            "impressions": 18950
        }
    )
    api_docs.add_model(engagement_metrics)
    
    # Error Response
    error_response = APIModel(
        name="ErrorResponse",
        type="object",
        description="Standard error response format",
        properties={
            "error": {
                "type": "string",
                "description": "Error type identifier"
            },
            "message": {
                "type": "string",
                "description": "Human-readable error message"
            },
            "details": {
                "type": "object",
                "description": "Additional error details"
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "When the error occurred"
            },
            "request_id": {
                "type": "string",
                "description": "Unique request identifier for tracking"
            }
        },
        required=["error", "message"],
        example={
            "error": "VALIDATION_ERROR",
            "message": "Invalid input parameters",
            "details": {
                "field": "topic",
                "issue": "Topic cannot be empty"
            },
            "timestamp": "2024-01-15T10:30:00Z",
            "request_id": "req_12345"
        }
    )
    api_docs.add_model(error_response)

def _add_api_endpoints(api_docs: APIDocumentation):
    """Add API endpoints to the documentation."""
    
    # Health Check
    health_check = APIEndpoint(
        path="/health",
        method="GET",
        summary="Health Check",
        description="Check the health status of the API service",
        tags=["system"],
        responses={
            "200": {
                "description": "Service is healthy",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "timestamp": {"type": "string"},
                                "version": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    )
    api_docs.add_endpoint(health_check)
    
    # Generate Caption
    generate_caption = APIEndpoint(
        path="/api/v10/captions/generate",
        method="POST",
        summary="Generate Instagram Caption",
        description="Generate an optimized Instagram caption based on content type, topic, and tone preferences",
        tags=["captions"],
        request_body={
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/CaptionGenerationRequest"}
                }
            }
        },
        responses={
            "200": {
                "description": "Caption generated successfully",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/CaptionResponse"}
                    }
                }
            },
            "400": {
                "description": "Bad request - invalid input parameters",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "401": {
                "description": "Unauthorized - invalid or missing authentication",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "429": {
                "description": "Rate limit exceeded",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            },
            "500": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(generate_caption)
    
    # Batch Generate Captions
    batch_generate = APIEndpoint(
        path="/api/v10/captions/batch-generate",
        method="POST",
        summary="Batch Generate Captions",
        description="Generate multiple captions in a single request for bulk content creation",
        tags=["captions"],
        request_body={
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "requests": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/CaptionGenerationRequest"},
                                "minItems": 1,
                                "maxItems": 10
                            }
                        },
                        "required": ["requests"]
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "Captions generated successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "captions": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/CaptionResponse"}
                                },
                                "total_generated": {"type": "integer"},
                                "processing_time": {"type": "number"}
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Bad request - invalid input parameters",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(batch_generate)
    
    # Optimize Hashtags
    optimize_hashtags = APIEndpoint(
        path="/api/v10/hashtags/optimize",
        method="POST",
        summary="Optimize Hashtags",
        description="Analyze and optimize hashtags for maximum reach and engagement",
        tags=["hashtags"],
        request_body={
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "competition_level": {
                                "type": "string",
                                "enum": ["low", "medium", "high"]
                            },
                            "hashtag_count": {
                                "type": "integer",
                                "minimum": 5,
                                "maximum": 30
                            }
                        },
                        "required": ["topic"]
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "Hashtags optimized successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "optimized_hashtags": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/HashtagAnalysis"}
                                },
                                "recommendations": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(optimize_hashtags)
    
    # Analyze Engagement
    analyze_engagement = APIEndpoint(
        path="/api/v10/analytics/engagement",
        method="POST",
        summary="Analyze Caption Engagement",
        description="Analyze the potential engagement of a caption before posting",
        tags=["engagement", "analytics"],
        request_body={
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "caption_text": {"type": "string"},
                            "hashtags": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "target_audience": {"type": "string"},
                            "content_type": {"type": "string"}
                        },
                        "required": ["caption_text"]
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "Engagement analysis completed",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "engagement_score": {"type": "number"},
                                "readability_score": {"type": "number"},
                                "sentiment_score": {"type": "number"},
                                "recommendations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(analyze_engagement)
    
    # Get Caption Templates
    get_templates = APIEndpoint(
        path="/api/v10/templates/captions",
        method="GET",
        summary="Get Caption Templates",
        description="Retrieve pre-built caption templates for various content types",
        tags=["templates"],
        parameters=[
            {
                "name": "category",
                "in": "query",
                "description": "Template category filter",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["fashion", "food", "travel", "business", "lifestyle", "fitness"]
                }
            },
            {
                "name": "tone",
                "in": "query",
                "description": "Template tone filter",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["casual", "professional", "humorous", "inspirational"]
                }
            },
            {
                "name": "limit",
                "in": "query",
                "description": "Maximum number of templates to return",
                "required": False,
                "schema": {"type": "integer", "minimum": 1, "maximum": 50}
            }
        ],
        responses={
            "200": {
                "description": "Templates retrieved successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "templates": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "template": {"type": "string"},
                                            "category": {"type": "string"},
                                            "tone": {"type": "string"},
                                            "usage_count": {"type": "integer"}
                                        }
                                    }
                                },
                                "total_count": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(get_templates)
    
    # Translate Caption
    translate_caption = APIEndpoint(
        path="/api/v10/captions/translate",
        method="POST",
        summary="Translate Caption",
        description="Translate a caption to different languages while maintaining context and tone",
        tags=["multilingual", "captions"],
        request_body={
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "caption_text": {"type": "string"},
                            "source_language": {"type": "string"},
                            "target_language": {"type": "string"},
                            "preserve_hashtags": {"type": "boolean"},
                            "cultural_adaptation": {"type": "boolean"}
                        },
                        "required": ["caption_text", "target_language"]
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "Caption translated successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "original_text": {"type": "string"},
                                "translated_text": {"type": "string"},
                                "source_language": {"type": "string"},
                                "target_language": {"type": "string"},
                                "confidence_score": {"type": "number"},
                                "cultural_notes": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(translate_caption)
    
    # Brand Voice Analysis
    brand_voice_analysis = APIEndpoint(
        path="/api/v10/branding/voice-analysis",
        method="POST",
        summary="Analyze Brand Voice",
        description="Analyze how well a caption aligns with brand voice guidelines",
        tags=["branding", "analytics"],
        request_body={
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "caption_text": {"type": "string"},
                            "brand_guidelines": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "industry": {"type": "string"}
                        },
                        "required": ["caption_text", "brand_guidelines"]
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "Brand voice analysis completed",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "alignment_score": {"type": "number"},
                                "voice_consistency": {"type": "number"},
                                "tone_match": {"type": "number"},
                                "recommendations": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(brand_voice_analysis)
    
    # Content Compliance Check
    compliance_check = APIEndpoint(
        path="/api/v10/compliance/check",
        method="POST",
        summary="Content Compliance Check",
        description="Check caption content for compliance with platform guidelines and brand safety",
        tags=["compliance", "safety"],
        request_body={
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "caption_text": {"type": "string"},
                            "platform": {
                                "type": "string",
                                "enum": ["instagram", "facebook", "tiktok", "linkedin"]
                            },
                            "industry": {"type": "string"},
                            "strict_mode": {"type": "boolean"}
                        },
                        "required": ["caption_text", "platform"]
                    }
                }
            }
        },
        responses={
            "200": {
                "description": "Compliance check completed",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "is_compliant": {"type": "boolean"},
                                "compliance_score": {"type": "number"},
                                "issues": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string"},
                                            "severity": {"type": "string"},
                                            "description": {"type": "string"},
                                            "suggestion": {"type": "string"}
                                        }
                                    }
                                },
                                "recommendations": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        security=[{"bearerAuth": []}]
    )
    api_docs.add_endpoint(compliance_check)

def main():
    """Main function to generate API documentation."""
    try:
        logger.info("Starting API documentation generation...")
        
        # Create API documentation
        api_docs = create_instagram_captions_api_docs()
        
        # Create output directory
        output_dir = Path("generated_docs")
        output_dir.mkdir(exist_ok=True)
        
        # Export all documentation formats
        success = api_docs.export_all_formats(str(output_dir))
        
        if success:
            # Get statistics
            stats = api_docs.get_statistics()
            logger.info("Documentation generation completed successfully!")
            logger.info(f"Generated {stats['total_endpoints']} endpoints")
            logger.info(f"Generated {stats['total_models']} data models")
            logger.info(f"Generated {stats['total_tags']} API tags")
            logger.info(f"Documentation saved to: {output_dir.absolute()}")
            
            # List generated files
            generated_files = list(output_dir.glob("*"))
            logger.info("Generated files:")
            for file_path in generated_files:
                logger.info(f"  - {file_path.name}")
        else:
            logger.error("Documentation generation failed!")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)






