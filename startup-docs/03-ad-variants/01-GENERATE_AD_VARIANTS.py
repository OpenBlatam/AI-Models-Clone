"""
Script para generar 1000 variantes de ads para Addiction Recovery AI
Ejecutar: python 01-GENERATE_AD_VARIANTS.py
"""

import json
import csv
from datetime import datetime

# Plantillas base
headlines_awareness = [
    "280 millones de personas luchan contra adicciones. Solo el 10% recibe ayuda.",
    "El 60% de las personas en recuperación tienen una recaída. Esto puede cambiar.",
    "$740 mil millones se pierden anualmente por adicciones. Hay una solución.",
    "¿Sientes que estás solo en tu lucha contra la adicción?",
    "La vergüenza no debería impedirte buscar ayuda.",
    "La primera IA especializada en recuperación de adicciones.",
    "Recuperación asistida por IA: el futuro del tratamiento.",
    "Ayuda disponible cuando la necesites, no cuando un terapeuta esté disponible.",
    "Crisis a las 3 AM? Nuestra IA está despierta.",
    "Tratamiento de adicciones desde $29/mes. Sin citas, sin estigma.",
    "Recuperación accesible para todos, sin importar dónde vivas.",
    "Tu recuperación, tu privacidad. 100% confidencial.",
    "Recuperación discreta. Nadie necesita saberlo.",
    "No más listas de espera. Ayuda inmediata disponible.",
    "Rompe el ciclo de recaídas con tecnología de vanguardia.",
    "Millones buscan ayuda. Pocos la encuentran. Eso está cambiando.",
    "La recuperación no debería costar $200 por sesión.",
    "Disponible en tu teléfono. Disponible en tu idioma. Disponible ahora.",
    "De la desesperación a la esperanza. Un mensaje de texto de distancia.",
    "Tu futuro sin adicción comienza con un click.",
]

descriptions_awareness = [
    "La recuperación no debería ser un privilegio. Conoce cómo la IA está haciendo el tratamiento accesible 24/7.",
    "Nuestra plataforma de IA reduce las recaídas en un 45%. Descubre cómo.",
    "Addiction Recovery AI ofrece tratamiento accesible y efectivo. Disponible 24/7.",
    "No estás solo. Nuestra IA está disponible 24/7 para apoyarte en cada paso de tu recuperación.",
    "Plataforma 100% privada y confidencial. Comienza tu recuperación desde casa.",
    "Tecnología de vanguardia que aprende de ti y se adapta a tu proceso único de recuperación.",
    "Disponible 24/7, personalizado y probado clínicamente. Descubre cómo funciona.",
    "Nuestra IA está lista para ti las 24 horas del día, los 7 días de la semana.",
    "Soporte inmediato cuando más lo necesitas. Sin citas, sin esperas.",
    "Más accesible que una sesión de terapia tradicional. Y disponible 24/7.",
    "Sin barreras geográficas. Sin listas de espera. Solo ayuda cuando la necesitas.",
    "Encriptación end-to-end. Cumplimiento HIPAA. Tu información nunca se comparte.",
    "Accede desde tu teléfono, en privado. Sin que nadie sepa que estás en tratamiento.",
    "Respuesta en minutos, no semanas. Tu recuperación no puede esperar.",
    "IA entrenada en millones de conversaciones de recuperación. Probada y efectiva.",
    "Únete a miles que están transformando sus vidas con ayuda de IA.",
    "El mismo nivel de cuidado, sin el costo ni las barreras.",
    "Habla en español, inglés, o portugués. Tu idioma, tu recuperación.",
    "Cuando la tentación llama, nuestra IA responde. Siempre.",
    "El primer paso es el más difícil. Te ayudamos a darlo.",
]

headlines_consideration = [
    "Reduce las recaídas en un 45% con nuestro plan personalizado de IA.",
    "Detección predictiva de recaídas con 85% de precisión.",
    "Asesoramiento 24/7 + Plan Personalizado + Comunidad de Apoyo.",
    "IA que aprende de ti y se adapta a tu progreso.",
    "4.8/5 estrellas. Únete a 5,000 personas en recuperación.",
    "78% de nuestros usuarios permanecen activos después de 6 meses.",
    "Plan personalizado basado en tu perfil único.",
    "Monitoreo continuo. Alertas proactivas. Soporte cuando lo necesitas.",
    "Comunidad de apoyo con moderación inteligente por IA.",
    "Integración con profesionales para casos complejos.",
    "Dashboard de progreso en tiempo real.",
    "Métricas que importan: días limpios, hitos alcanzados, riesgo de recaída.",
    "Recursos adaptados a tu tipo de adicción.",
    "Terapia cognitivo-conductual potenciada por IA.",
    "Sistema de recompensas que celebra cada logro.",
    "Grupos de apoyo virtuales disponibles 24/7.",
    "Acceso a profesionales certificados cuando lo necesites.",
    "Historial completo y privado de tu recuperación.",
    "Notificaciones inteligentes que te mantienen en el camino.",
    "Recursos educativos personalizados para tu situación.",
]

descriptions_consideration = [
    "Cada plan es único, adaptado a ti. Basado en ciencia, potenciado por IA.",
    "Nuestra IA detecta señales de riesgo antes de que sea demasiado tarde.",
    "Todo lo que necesitas para tu recuperación en una sola plataforma.",
    "Cada conversación mejora tu plan. Cada día te acerca más a la recuperación.",
    "Lee lo que dicen nuestros usuarios sobre cómo cambió sus vidas.",
    "No es solo una app. Es una comunidad que te apoya en cada paso.",
    "Generado por IA basado en tu perfil psicológico y comportamiento.",
    "Nunca estarás solo. Nuestra IA te acompaña en cada momento difícil.",
    "Conecta con personas que entienden tu lucha. Sin juicios, solo apoyo.",
    "Para casos que requieren atención humana, conectamos con expertos.",
    "Visualiza tu progreso día a día. Cada pequeño paso cuenta.",
    "Datos que te empoderan. Conocimiento que transforma.",
    "Alcohol, drogas, juego, tecnología. Especializado en tu adicción.",
    "Técnicas probadas, entregadas de manera personalizada por IA.",
    "Cada día limpio es una victoria. Te ayudamos a celebrarlas todas.",
    "Únete a grupos temáticos. Encuentra tu tribu.",
    "Terapeutas certificados disponibles para sesiones virtuales.",
    "Tu historia de recuperación, guardada de forma segura y privada.",
    "Recordatorios que te motivan, no que te molestan.",
    "Artículos, videos, ejercicios. Todo adaptado a tu progreso.",
]

headlines_conversion = [
    "7 días gratis. Sin tarjeta de crédito. Sin compromiso.",
    "20% OFF primeros 3 meses. Solo para nuevos usuarios.",
    "Solo quedan 50 spots este mes. No te quedes fuera.",
    "Precio aumenta el próximo mes. Bloquea tu tarifa actual.",
    "Únete a 5,000 personas que están transformando sus vidas.",
    "Garantía de 30 días. Si no funciona, te devolvemos tu dinero.",
    "Comienza tu recuperación hoy. Sin esperas, sin excusas.",
    "El mejor momento para empezar es ahora.",
    "Tu futuro sin adicción comienza con un click.",
    "No esperes a tocar fondo. La ayuda está aquí.",
    "Oferta de lanzamiento: 20% off + mes gratis.",
    "Últimos días para precio especial de fundador.",
    "Más de 1,000 personas se unieron esta semana.",
    "Prueba gratis. Cancela cuando quieras. Sin preguntas.",
    "Acceso inmediato. Comienza en menos de 5 minutos.",
    "Únete ahora y obtén 2 meses gratis.",
    "Oferta limitada: $29/mes por tiempo limitado.",
    "No dejes que otra recaída te detenga.",
    "Tu recuperación no puede esperar. Nosotros tampoco.",
    "Empezar es fácil. Mantenerse es difícil. Te ayudamos con ambos.",
]

descriptions_conversion = [
    "Prueba nuestra plataforma completa sin riesgo. Cancela cuando quieras.",
    "Oferta limitada. Comienza tu recuperación hoy con descuento especial.",
    "Nuestro programa personalizado tiene cupos limitados. Asegura tu lugar.",
    "Únete ahora y mantén el precio de lanzamiento para siempre.",
    "Lee sus historias. Inspírate. Únete a ellos.",
    "Estamos tan seguros que te funcionará que te devolvemos tu dinero si no.",
    "Regístrate en 2 minutos. Comienza tu recuperación en 5.",
    "Cada día que esperas es un día más de lucha innecesaria.",
    "Click aquí. Regístrate. Comienza. Es así de simple.",
    "La ayuda está a un click de distancia. No la dejes pasar.",
    "Doble beneficio: ahorra dinero y transforma tu vida.",
    "Esta es tu última oportunidad para este precio especial.",
    "La comunidad crece. El apoyo se fortalece. Únete ahora.",
    "Sin compromisos ocultos. Sin sorpresas. Solo resultados.",
    "En menos tiempo del que tardas en leer esto, puedes estar registrado.",
    "Oferta exclusiva para nuevos miembros. No la dejes pasar.",
    "Precio especial solo por tiempo limitado. Actúa ahora.",
    "Cada recaída es una oportunidad perdida. No dejes que pase otra vez.",
    "Estamos aquí, listos para ayudarte. Solo necesitas dar el primer paso.",
    "El registro toma 2 minutos. La recuperación toma tiempo. Empecemos.",
]

ctas = [
    "Aprende Más",
    "Descubre Cómo",
    "Conoce Más",
    "Habla con Nuestra IA",
    "Empezar Ahora",
    "Ver Demo",
    "Probar Gratis",
    "Ver Cómo Funciona",
    "Ver Todas las Features",
    "Probar Demo",
    "Ver Testimonios",
    "Unirse Ahora",
    "Empezar Prueba Gratis",
    "Aprovechar Oferta",
    "Reservar Ahora",
    "Completar Registro",
    "Hablar con Especialista",
    "Agendar Demo",
    "Obtener Ayuda",
    "Comienza Ahora",
]

platforms = ["Facebook", "Instagram", "Google", "LinkedIn", "TikTok", "YouTube"]

def generate_ad_variant(ad_id, category, headline, description, cta, platform):
    """Genera una variante de ad"""
    return {
        "ad_id": ad_id,
        "category": category,
        "platform": platform,
        "headline": headline,
        "description": description,
        "cta": cta,
        "created_at": datetime.now().isoformat(),
        "status": "draft"
    }

def generate_all_variants():
    """Genera todas las variantes de ads"""
    ads = []
    ad_id = 1
    
    # Awareness Ads (300)
    for i in range(300):
        headline = headlines_awareness[i % len(headlines_awareness)]
        description = descriptions_awareness[i % len(descriptions_awareness)]
        cta = ctas[i % len(ctas)]
        platform = platforms[i % len(platforms)]
        ads.append(generate_ad_variant(
            ad_id, "Awareness", headline, description, cta, platform
        ))
        ad_id += 1
    
    # Consideration Ads (300)
    for i in range(300):
        headline = headlines_consideration[i % len(headlines_consideration)]
        description = descriptions_consideration[i % len(descriptions_consideration)]
        cta = ctas[i % len(ctas)]
        platform = platforms[i % len(platforms)]
        ads.append(generate_ad_variant(
            ad_id, "Consideration", headline, description, cta, platform
        ))
        ad_id += 1
    
    # Conversion Ads (200)
    for i in range(200):
        headline = headlines_conversion[i % len(headlines_conversion)]
        description = descriptions_conversion[i % len(descriptions_conversion)]
        cta = ctas[i % len(ctas)]
        platform = platforms[i % len(platforms)]
        ads.append(generate_ad_variant(
            ad_id, "Conversion", headline, description, cta, platform
        ))
        ad_id += 1
    
    # Retargeting Ads (100)
    for i in range(100):
        headline = f"Tu recuperación te está esperando. {headlines_conversion[i % len(headlines_conversion)]}"
        description = descriptions_conversion[i % len(descriptions_conversion)]
        cta = ctas[i % len(ctas)]
        platform = platforms[i % len(platforms)]
        ads.append(generate_ad_variant(
            ad_id, "Retargeting", headline, description, cta, platform
        ))
        ad_id += 1
    
    # Video Ads Scripts (100)
    for i in range(100):
        script = f"""
Video Ad Script {ad_id}:
[0-5s] Hook: "{headlines_awareness[i % len(headlines_awareness)]}"
[5-15s] Problema: "{descriptions_awareness[i % len(descriptions_awareness)]}"
[15-30s] Solución: "{headlines_consideration[i % len(headlines_consideration)]}"
[30-45s] CTA: "{ctas[i % len(ctas)]}"
[45-60s] Brand: "Addiction Recovery AI"
"""
        ads.append({
            "ad_id": ad_id,
            "category": "Video",
            "platform": platforms[i % len(platforms)],
            "script": script.strip(),
            "created_at": datetime.now().isoformat(),
            "status": "draft"
        })
        ad_id += 1
    
    return ads

def save_to_json(ads, filename):
    """Guarda ads en formato JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ads, f, indent=2, ensure_ascii=False)

def save_to_csv(ads, filename):
    """Guarda ads en formato CSV"""
    if not ads:
        return
    
    fieldnames = ["ad_id", "category", "platform", "headline", "description", "cta", "status"]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ad in ads:
            if ad.get("script"):
                continue  # Skip video ads in CSV
            row = {
                "ad_id": ad["ad_id"],
                "category": ad["category"],
                "platform": ad["platform"],
                "headline": ad.get("headline", ""),
                "description": ad.get("description", ""),
                "cta": ad.get("cta", ""),
                "status": ad["status"]
            }
            writer.writerow(row)

if __name__ == "__main__":
    print("Generando 1000 variantes de ads...")
    ads = generate_all_variants()
    print(f"Generadas {len(ads)} variantes")
    
    # Guardar en JSON
    save_to_json(ads, "02-ALL_AD_VARIANTS.json")
    print("Guardado en JSON: 02-ALL_AD_VARIANTS.json")
    
    # Guardar en CSV (solo ads de texto)
    text_ads = [ad for ad in ads if not ad.get("script")]
    save_to_csv(text_ads, "03-ALL_AD_VARIANTS.csv")
    print(f"Guardado en CSV: 03-ALL_AD_VARIANTS.csv ({len(text_ads)} ads de texto)")
    
    # Guardar video scripts por separado
    video_ads = [ad for ad in ads if ad.get("script")]
    with open("04-VIDEO_AD_SCRIPTS.txt", 'w', encoding='utf-8') as f:
        for ad in video_ads:
            f.write(f"\n{'='*80}\n")
            f.write(f"Ad ID: {ad['ad_id']}\n")
            f.write(f"Platform: {ad['platform']}\n")
            f.write(f"{ad['script']}\n")
    print(f"Guardado scripts de video: 04-VIDEO_AD_SCRIPTS.txt ({len(video_ads)} scripts)")
    
    print("\n[OK] Completado! 1000 variantes de ads generadas.")

