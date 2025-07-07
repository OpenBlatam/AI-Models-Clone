#!/usr/bin/env python3
"""
Script de prueba para el servicio de análisis SEO con LangChain
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

from features.seo.service import SEOService
from features.seo.models import SEOScrapeRequest

def test_seo_analysis():
    """Prueba el análisis SEO con una URL de ejemplo"""
    
    # Configurar API key de OpenAI (opcional para pruebas básicas)
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY no configurada. El análisis será básico.")
    
    # URL de prueba
    test_url = "https://www.google.com"
    
    print(f"🔍 Analizando SEO de: {test_url}")
    print("=" * 50)
    
    try:
        # Crear request
        request = SEOScrapeRequest(url=test_url)
        
        # Realizar análisis
        response = SEOService.scrape(request)
        
        if response.success:
            data = response.data
            
            print("✅ Análisis completado exitosamente!")
            print()
            
            # Mostrar resultados principales
            print("📊 RESULTADOS DEL ANÁLISIS SEO")
            print("-" * 30)
            print(f"Título: {data.title}")
            print(f"Meta descripción: {data.meta_description[:100]}...")
            print(f"Puntuación SEO: {data.seo_score}/100")
            print(f"Tiempo de carga: {data.load_time:.2f}s")
            print(f"Velocidad: {data.page_speed}")
            print(f"Compatible móvil: {'✅' if data.mobile_friendly else '❌'}")
            print()
            
            # Headers
            print("📝 ESTRUCTURA DE HEADERS")
            print("-" * 30)
            print(f"H1 tags: {len(data.h1_tags)}")
            for h1 in data.h1_tags[:3]:  # Mostrar solo los primeros 3
                print(f"  - {h1}")
            print(f"H2 tags: {len(data.h2_tags)}")
            print(f"H3 tags: {len(data.h3_tags)}")
            print()
            
            # Imágenes y enlaces
            print("🖼️  CONTENIDO MULTIMEDIA")
            print("-" * 30)
            print(f"Imágenes: {len(data.images)}")
            images_with_alt = len([img for img in data.images if img.get('alt')])
            print(f"  - Con alt text: {images_with_alt}")
            print(f"Enlaces: {len(data.links)}")
            internal_links = len([link for link in data.links if link.get('is_internal')])
            print(f"  - Internos: {internal_links}")
            print(f"  - Externos: {len(data.links) - internal_links}")
            print()
            
            # Palabras clave
            if data.keywords:
                print("🔑 PALABRAS CLAVE")
                print("-" * 30)
                print(f"Keywords: {', '.join(data.keywords)}")
                print()
            
            # Recomendaciones
            if data.recommendations:
                print("💡 RECOMENDACIONES")
                print("-" * 30)
                for i, rec in enumerate(data.recommendations, 1):
                    print(f"{i}. {rec}")
                print()
            
            # Problemas técnicos
            if data.technical_issues:
                print("⚠️  PROBLEMAS TÉCNICOS")
                print("-" * 30)
                for i, issue in enumerate(data.technical_issues, 1):
                    print(f"{i}. {issue}")
                print()
            
            # Resumen del análisis
            if response.analysis_summary:
                print("📋 RESUMEN DEL ANÁLISIS")
                print("-" * 30)
                print(response.analysis_summary)
                print()
            
            # Tags de redes sociales
            if data.social_media_tags:
                print("📱 TAGS DE REDES SOCIALES")
                print("-" * 30)
                for key, value in data.social_media_tags.items():
                    print(f"{key}: {value[:50]}...")
                print()
            
            print("=" * 50)
            print("🎉 Análisis SEO completado!")
            
        else:
            print(f"❌ Error en el análisis: {response.error}")
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

def test_multiple_urls():
    """Prueba el análisis con múltiples URLs"""
    
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.stackoverflow.com"
    ]
    
    print("🔍 ANÁLISIS DE MÚLTIPLES URLs")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\n📊 Analizando: {url}")
        print("-" * 30)
        
        try:
            request = SEOScrapeRequest(url=url)
            response = SEOService.scrape(request)
            
            if response.success:
                data = response.data
                print(f"✅ Puntuación SEO: {data.seo_score}/100")
                print(f"⏱️  Tiempo de carga: {data.load_time:.2f}s")
                print(f"📱 Móvil: {'✅' if data.mobile_friendly else '❌'}")
                print(f"📝 Título: {data.title[:50]}...")
            else:
                print(f"❌ Error: {response.error}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del servicio SEO con LangChain")
    print()
    
    # Prueba individual
    test_seo_analysis()
    
    print("\n" + "="*50 + "\n")
    
    # Prueba múltiple (comentada para evitar demasiadas llamadas)
    # test_multiple_urls()
    
    print("✅ Pruebas completadas!") 