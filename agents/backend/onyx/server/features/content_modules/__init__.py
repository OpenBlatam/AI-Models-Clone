"""
📝 CONTENT MODULES - Organized Content Generation
=================================================

Organiza todos los generadores de contenido por categorías:
- 📱 Social Media: Instagram, Facebook, Twitter
- 📰 Editorial: Blog posts, Articles  
- 💰 Marketing: Ads, Copy, Key messages
- 🛍️ E-commerce: Product descriptions, Reviews
- 📹 Multimedia: Videos, Captions
- 🔧 Technical: SEO, Documentation
"""

__version__ = "1.0.0"
__description__ = "Organized Content Generation Modules"

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# 📱 SOCIAL MEDIA MODULES
# =============================================================================

class SocialMediaModules:
    """Módulos para redes sociales."""
    
    @staticmethod
    def get_available_modules():
        return {
            'instagram_captions': {
                'path': '../instagram_captions',
                'description': 'Instagram caption generation',
                'status': 'available'
            },
            'facebook_posts': {
                'path': '../facebook_posts', 
                'description': 'Facebook post generation',
                'status': 'available'
            }
        }

# =============================================================================
# 📰 EDITORIAL MODULES  
# =============================================================================

class EditorialModules:
    """Módulos editoriales."""
    
    @staticmethod
    def get_available_modules():
        return {
            'blog_posts': {
                'path': '../blog_posts',
                'description': 'Blog post generation',
                'status': 'available'
            },
            'copywriting': {
                'path': '../copywriting',
                'description': 'Professional copywriting',
                'status': 'available'
            }
        }

# =============================================================================
# 💰 MARKETING MODULES
# =============================================================================

class MarketingModules:
    """Módulos de marketing."""
    
    @staticmethod
    def get_available_modules():
        return {
            'ads': {
                'path': '../ads',
                'description': 'Advertisement generation',
                'status': 'available'
            },
            'key_messages': {
                'path': '../key_messages',
                'description': 'Key message creation',
                'status': 'available'
            }
        }

# =============================================================================
# 🛍️ E-COMMERCE MODULES
# =============================================================================

class EcommerceModules:
    """Módulos de e-commerce."""
    
    @staticmethod
    def get_available_modules():
        return {
            'product_descriptions': {
                'path': '../product_descriptions',
                'description': 'AI product description generation',
                'status': 'available',
                'features': ['transformers', 'pytorch', 'seo_optimization']
            }
        }

# =============================================================================
# 📹 MULTIMEDIA MODULES
# =============================================================================

class MultimediaModules:
    """Módulos multimedia."""
    
    @staticmethod
    def get_available_modules():
        return {
            'ai_video': {
                'path': '../ai_video',
                'description': 'AI video content generation',
                'status': 'available'
            },
            'video': {
                'path': '../video',
                'description': 'Video processing and generation',
                'status': 'available'
            }
        }

# =============================================================================
# 🔧 TECHNICAL MODULES
# =============================================================================

class TechnicalModules:
    """Módulos técnicos."""
    
    @staticmethod
    def get_available_modules():
        return {
            'seo': {
                'path': '../seo',
                'description': 'SEO content optimization',
                'status': 'available'
            },
            'image_process': {
                'path': '../image_process',
                'description': 'Image processing and generation',
                'status': 'available'
            }
        }

# =============================================================================
# 🎯 UNIFIED CONTENT MANAGER
# =============================================================================

class ContentModuleManager:
    """
    Gestor unificado de todos los módulos de contenido.
    
    Proporciona acceso organizado a todos los generadores por categoría.
    """
    
    def __init__(self):
        self.social_media = SocialMediaModules()
        self.editorial = EditorialModules()
        self.marketing = MarketingModules()
        self.ecommerce = EcommerceModules()
        self.multimedia = MultimediaModules()
        self.technical = TechnicalModules()
    
    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene todos los módulos organizados por categoría."""
        return {
            'social_media': self.social_media.get_available_modules(),
            'editorial': self.editorial.get_available_modules(),
            'marketing': self.marketing.get_available_modules(),
            'ecommerce': self.ecommerce.get_available_modules(),
            'multimedia': self.multimedia.get_available_modules(),
            'technical': self.technical.get_available_modules()
        }
    
    def get_module_by_name(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Busca un módulo específico por nombre."""
        all_modules = self.get_all_modules()
        
        for category, modules in all_modules.items():
            if module_name in modules:
                return {
                    'category': category,
                    'module_info': modules[module_name]
                }
        
        return None
    
    def get_modules_by_category(self, category: str) -> Dict[str, Any]:
        """Obtiene módulos de una categoría específica."""
        all_modules = self.get_all_modules()
        return all_modules.get(category, {})
    
    def get_featured_modules(self) -> Dict[str, Any]:
        """Obtiene los módulos destacados."""
        return {
            'ai_powered': {
                'product_descriptions': 'AI product descriptions with Transformers',
                'enterprise_api': 'Ultra-fast enterprise processing with AI'
            },
            'social_media': {
                'instagram_captions': 'Instagram caption generation',
                'facebook_posts': 'Facebook post creation'
            },
            'marketing': {
                'ads': 'Advertisement generation',
                'copywriting': 'Professional copywriting'
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de los módulos."""
        all_modules = self.get_all_modules()
        
        total_modules = sum(len(modules) for modules in all_modules.values())
        categories = len(all_modules)
        
        return {
            'total_modules': total_modules,
            'categories': categories,
            'modules_by_category': {
                category: len(modules) 
                for category, modules in all_modules.items()
            },
            'featured_count': len(self.get_featured_modules()),
            'ai_powered_modules': ['product_descriptions', 'enterprise_api']
        }


# =============================================================================
# 🎯 QUICK ACCESS FUNCTIONS
# =============================================================================

def get_content_manager() -> ContentModuleManager:
    """Obtiene el gestor de módulos de contenido."""
    return ContentModuleManager()

def list_all_modules() -> Dict[str, Dict[str, Any]]:
    """Lista todos los módulos disponibles."""
    manager = ContentModuleManager()
    return manager.get_all_modules()

def find_module(name: str) -> Optional[Dict[str, Any]]:
    """Encuentra un módulo específico."""
    manager = ContentModuleManager()
    return manager.get_module_by_name(name)

def get_category_modules(category: str) -> Dict[str, Any]:
    """Obtiene módulos de una categoría."""
    manager = ContentModuleManager()
    return manager.get_modules_by_category(category)

# =============================================================================
# 📊 MODULE USAGE EXAMPLES
# =============================================================================

def get_usage_examples() -> Dict[str, str]:
    """Ejemplos de uso del sistema de módulos."""
    return {
        'list_all': '''
# 📋 Listar todos los módulos
from content_modules import list_all_modules

modules = list_all_modules()
for category, mods in modules.items():
    print(f"{category}: {list(mods.keys())}")
        ''',
        
        'find_specific': '''
# 🔍 Buscar módulo específico
from content_modules import find_module

module_info = find_module('product_descriptions')
print(f"Found in category: {module_info['category']}")
        ''',
        
        'by_category': '''
# 📱 Obtener módulos por categoría
from content_modules import get_category_modules

social_modules = get_category_modules('social_media')
ecommerce_modules = get_category_modules('ecommerce')
        ''',
        
        'full_manager': '''
# 🎯 Usar el gestor completo
from content_modules import get_content_manager

manager = get_content_manager()
stats = manager.get_statistics()
featured = manager.get_featured_modules()
        '''
    }

# =============================================================================
# 🌟 EXPORTS
# =============================================================================

__all__ = [
    # Main manager
    "ContentModuleManager",
    "get_content_manager",
    
    # Category managers
    "SocialMediaModules",
    "EditorialModules", 
    "MarketingModules",
    "EcommerceModules",
    "MultimediaModules",
    "TechnicalModules",
    
    # Quick access functions
    "list_all_modules",
    "find_module",
    "get_category_modules",
    "get_usage_examples"
] 