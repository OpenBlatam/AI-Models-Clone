"""
Funciones de sugerencias creativas para videos AI según emoción/tono.
"""
from typing import List

def suggest_music(emotion: str) -> List[str]:
    """Devuelve una lista de sugerencias de música según la emoción."""
    return {
        "alegre": ["upbeat_pop.mp3", "happy_ukulele.mp3", "energetic_dance.mp3"],
        "serio": ["soft_piano.mp3", "ambient_strings.mp3"],
        "juvenil": ["modern_beat.mp3", "trap_urban.mp3"],
        "neutral": ["ambient_background.mp3", "corporate_soft.mp3"],
        "triste": ["sad_strings.mp3", "slow_piano.mp3"],
        "emocionante": ["epic_orchestra.mp3", "action_drums.mp3"]
    }.get(emotion, ["ambient_background.mp3"])

def suggest_visual_styles(emotion: str) -> List[str]:
    """Devuelve una lista de sugerencias de estilos visuales según la emoción."""
    return {
        "alegre": ["colores vivos, animaciones rápidas", "estilo cartoon, tipografía bold"],
        "serio": ["tonos sobrios, transiciones suaves", "estilo documental, imágenes reales"],
        "juvenil": ["estilo moderno, gráficos dinámicos", "colores neón, efectos glitch"],
        "neutral": ["estilo limpio, minimalista", "paleta neutra, transiciones simples"],
        "triste": ["colores fríos, ritmo lento", "imágenes en azul/gris, desenfoque"],
        "emocionante": ["efectos de impacto, cortes rápidos", "luces intensas, cámara rápida"]
    }.get(emotion, ["estilo limpio, minimalista"])

def suggest_sound_effects(emotion: str) -> List[str]:
    """Devuelve una lista de sugerencias de efectos de sonido según la emoción."""
    return {
        "alegre": ["applause.wav", "ding.wav", "laugh.wav"],
        "serio": ["soft_whoosh.wav", "page_turn.wav"],
        "juvenil": ["pop_cork.wav", "snap.wav"],
        "neutral": ["click.wav", "ambient_noise.wav"],
        "triste": ["sigh.wav", "rain.wav"],
        "emocionante": ["explosion.wav", "cheer.wav"]
    }.get(emotion, ["click.wav"])

def suggest_transitions(emotion: str) -> List[str]:
    """Devuelve una lista de sugerencias de transiciones visuales según la emoción."""
    return {
        "alegre": ["bounce", "spin", "slide_right"],
        "serio": ["fade", "cross_dissolve"],
        "juvenil": ["glitch", "zoom_in"],
        "neutral": ["cut", "fade"],
        "triste": ["blur", "slow_fade"],
        "emocionante": ["flash", "quick_cut"]
    }.get(emotion, ["cut"]) 