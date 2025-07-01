# Onyx Ads Module

This module provides functionality for generating ads, removing backgrounds from images, and tracking analytics.

## Features

- Ads Generation
  - Generate ads from prompts
  - Generate brand kits
  - Generate custom content
- Background Removal
  - Remove backgrounds from images
  - Support for PNG and JPEG formats
  - Automatic image resizing
- Analytics
  - Track ads performance
  - Store metrics
  - Query analytics data

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the environment variables:
```bash
# Storage settings
ADS_STORAGE_PATH=storage/ads
ADS_STORAGE_URL=/storage/ads

# Image processing settings
ADS_MAX_IMAGE_SIZE=256
ADS_JPEG_QUALITY=90

# LLM settings
ADS_LLM_MODEL=gpt-4
ADS_LLM_TEMPERATURE=0.7
ADS_LLM_MAX_TOKENS=2000

# Analytics settings
ADS_ANALYTICS_ENABLED=true
ADS_ANALYTICS_RETENTION_DAYS=90
```

## Usage

### Generate Ads

```python
from onyx.server.features.ads import AdsService

ads_service = AdsService()
result = await ads_service.generate_ads(
    prompt="Generate an ad for a new product",
    type="ads"
)
```

### Remove Background

```python
from onyx.server.features.ads import AdsService

ads_service = AdsService()
result = await ads_service.remove_background(
    image_url="https://example.com/image.jpg"
)
```

### Track Analytics

```python
from onyx.server.features.ads import AdsDBService

analytics = await AdsDBService.create_ads_analytics(
    user_id=1,
    ads_generation_id=1,
    metrics={
        "impressions": 1000,
        "clicks": 50,
        "conversions": 5
    }
)
```

## API Endpoints

### Ads Generation

- `POST /ads/generate` - Generate ads
- `GET /ads/list` - List ads generations
- `GET /ads/{ads_id}` - Get specific ads generation
- `DELETE /ads/{ads_id}` - Delete ads generation

### Background Removal

- `POST /ads/remove-background` - Remove background from image
- `GET /ads/background-removals` - List background removals
- `GET /ads/background-removals/{removal_id}` - Get specific background removal
- `DELETE /ads/background-removals/{removal_id}` - Delete background removal

### Analytics

- `POST /ads/analytics` - Track analytics
- `GET /ads/analytics` - List analytics
- `GET /ads/analytics/{analytics_id}` - Get specific analytics

## Database Schema

### AdsGeneration

- `id` - Primary key
- `user_id` - Foreign key to User
- `url` - URL of the generated content
- `type` - Type of content (ads, brand-kit, custom)
- `prompt` - Prompt used for generation
- `content` - Generated content
- `metadata` - Additional metadata
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `is_deleted` - Soft delete flag

### BackgroundRemoval

- `id` - Primary key
- `user_id` - Foreign key to User
- `original_image_url` - URL of original image
- `processed_image_url` - URL of processed image
- `metadata` - Additional metadata
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `is_deleted` - Soft delete flag

### AdsAnalytics

- `id` - Primary key
- `user_id` - Foreign key to User
- `ads_generation_id` - Foreign key to AdsGeneration
- `metrics` - Analytics metrics
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 