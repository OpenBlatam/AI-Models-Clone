# Static Content Directory

This directory contains static files served by the HeyGen AI API.

## Directory Structure

```
static/
├── css/                    # Stylesheets
│   ├── main.css           # Main application styles
│   ├── components.css     # Component-specific styles
│   └── themes/            # Theme variations
│       ├── light.css
│       └── dark.css
├── js/                    # JavaScript files
│   ├── main.js           # Main application script
│   ├── api.js            # API client utilities
│   └── components/       # Component scripts
│       ├── video-player.js
│       └── analytics.js
├── images/               # Image assets
│   ├── logo.png         # Application logo
│   ├── icons/           # Icon files
│   │   ├── play.svg
│   │   ├── pause.svg
│   │   └── download.svg
│   └── backgrounds/     # Background images
├── fonts/               # Custom fonts
│   ├── roboto.woff2
│   └── opensans.woff2
├── docs/                # Documentation files
│   ├── api-docs.html    # API documentation
│   └── user-guide.html  # User guide
└── templates/           # HTML templates
    ├── email/           # Email templates
    │   ├── welcome.html
    │   └── notification.html
    └── reports/         # Report templates
        └── analytics.html
```

## Usage

Static files are served at `/static/` endpoint and can be accessed directly:

- CSS: `/static/css/main.css`
- JavaScript: `/static/js/main.js`
- Images: `/static/images/logo.png`
- Documentation: `/static/docs/api-docs.html`

## File Organization

- **CSS**: Organized by functionality with theme support
- **JavaScript**: Modular structure with API utilities
- **Images**: Categorized by type (icons, backgrounds, etc.)
- **Fonts**: Web-optimized font files
- **Docs**: Static documentation and guides
- **Templates**: Reusable HTML templates for emails and reports

## Development

When adding new static files:

1. Place files in appropriate subdirectories
2. Update this README if adding new categories
3. Ensure files are optimized for web delivery
4. Use consistent naming conventions
5. Consider caching strategies for production 