"""
Función mejorada para evaluar respuestas basándose en palabras clave esperadas.

Este módulo evalúa si las respuestas contienen las palabras clave esperadas
y genera un reporte detallado con los prompts que no encontraron ninguna keyword.

Mejoras incluidas:
- Búsqueda de palabras completas (opcional)
- Resultados detallados por prompt
- Estadísticas adicionales
- Reporte mejorado con más información
"""

import re
from typing import List, Dict, Any


def evaluate_responses(
    pairs: List[Dict[str, Any]], 
    word_boundary: bool = False,
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Evalúa respuestas verificando la presencia de palabras clave esperadas.
    
    Recorre cada par en la lista y:
    - Verifica si cada palabra clave en expected_keywords aparece en response
    - Asigna un puntaje de 1 por palabra clave encontrada
    - Calcula estadísticas totales y detalladas
    
    Args:
        pairs: Lista de diccionarios con la estructura:
            {
                "prompt": str,
                "response": str,
                "expected_keywords": List[str]
            }
        word_boundary: Si es True, busca palabras completas (evita matches parciales)
        case_sensitive: Si es True, la búsqueda es case-sensitive
    
    Returns:
        Dict con las siguientes claves:
            - total_prompts: Número total de prompts evaluados
            - total_keywords: Número total de keywords esperadas (suma de todas)
            - keywords_found: Número total de keywords encontradas
            - accuracy: Ratio de keywords encontradas vs total (0.0 a 1.0)
            - prompts_with_zero_keywords: Lista de prompts que obtuvieron 0 keywords encontrados
            - per_prompt_results: Lista de resultados detallados por cada prompt
            - average_score_per_prompt: Score promedio por prompt
    """
    # Inicializar contadores
    total_prompts = 0
    total_keywords = 0
    keywords_found = 0
    
    # Lista para almacenar prompts con 0 keywords encontradas
    prompts_with_zero_keywords = []
    
    # Lista para resultados detallados por prompt
    per_prompt_results = []
    
    # Recorrer cada par prompt/response
    for pair_idx, pair in enumerate(pairs):
        # Validar que el par sea un diccionario
        if not isinstance(pair, dict):
            continue
        
        # Extraer datos del par
        prompt = pair.get("prompt", "")
        response = pair.get("response", "")
        expected_keywords = pair.get("expected_keywords", [])
        
        # Validar que tenemos los datos necesarios
        if not prompt or not response or not expected_keywords:
            continue
        
        # Incrementar contador de prompts
        total_prompts += 1
        
        # Preparar texto para búsqueda según configuración
        if case_sensitive:
            response_text = response
        else:
            response_text = response.lower()
        
        # Contador de keywords encontradas en este prompt
        found_count = 0
        found_keywords_list = []
        missing_keywords_list = []
        
        # Verificar cada palabra clave esperada
        for keyword in expected_keywords:
            # Saltar keywords vacías
            if not keyword or not keyword.strip():
                continue
            
            # Incrementar contador total de keywords
            total_keywords += 1
            
            # Preparar keyword para búsqueda
            if case_sensitive:
                keyword_search = keyword
            else:
                keyword_search = keyword.lower()
            
            # Verificar si la keyword aparece en la respuesta
            keyword_found = False
            
            if word_boundary:
                # Búsqueda de palabra completa usando límites de palabra
                pattern = r'\b' + re.escape(keyword_search) + r'\b'
                keyword_found = bool(re.search(pattern, response_text))
            else:
                # Búsqueda simple de substring
                keyword_found = keyword_search in response_text
            
            if keyword_found:
                # Keyword encontrada: asignar puntaje de 1
                found_count += 1
                keywords_found += 1
                found_keywords_list.append(keyword)
            else:
                missing_keywords_list.append(keyword)
        
        # Calcular score para este prompt (0.0 a 1.0)
        score = found_count / len(expected_keywords) if expected_keywords else 0.0
        
        # Guardar resultado detallado de este prompt
        prompt_result = {
            "prompt_index": pair_idx,
            "prompt": prompt,
            "response": response,
            "expected_keywords": expected_keywords,
            "found_keywords": found_keywords_list,
            "missing_keywords": missing_keywords_list,
            "found_count": found_count,
            "total_keywords": len(expected_keywords),
            "score": score
        }
        per_prompt_results.append(prompt_result)
        
        # Si no se encontró ninguna keyword, agregar a la lista de problemas
        if found_count == 0:
            prompts_with_zero_keywords.append({
                "prompt": prompt,
                "response": response,
                "expected_keywords": expected_keywords,
                "prompt_index": pair_idx
            })
    
    # Calcular accuracy: keywords_found / total_keywords
    accuracy = keywords_found / total_keywords if total_keywords > 0 else 0.0
    
    # Calcular score promedio por prompt
    if per_prompt_results:
        average_score = sum(r["score"] for r in per_prompt_results) / len(per_prompt_results)
    else:
        average_score = 0.0
    
    # Crear diccionario de resumen mejorado
    summary = {
        "total_prompts": total_prompts,
        "total_keywords": total_keywords,
        "keywords_found": keywords_found,
        "keywords_missing": total_keywords - keywords_found,
        "accuracy": accuracy,
        "average_score_per_prompt": average_score,
        "prompts_with_zero_keywords": prompts_with_zero_keywords,
        "per_prompt_results": per_prompt_results
    }
    
    return summary


def generate_report(summary: Dict[str, Any], detailed: bool = False) -> str:
    """
    Genera un reporte imprimible con los prompts que obtuvieron 0 keywords encontrados.
    
    Args:
        summary: Diccionario de resumen retornado por evaluate_responses
        detailed: Si es True, incluye resultados detallados de cada prompt
    
    Returns:
        String con el reporte formateado
    """
    report_lines = []
    
    # Encabezado del reporte
    report_lines.append("=" * 80)
    report_lines.append("REPORTE DE EVALUACIÓN DE RESPUESTAS")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Estadísticas generales
    report_lines.append("ESTADÍSTICAS GENERALES:")
    report_lines.append("-" * 80)
    report_lines.append(f"Total de prompts evaluados: {summary['total_prompts']}")
    report_lines.append(f"Total de keywords esperadas: {summary['total_keywords']}")
    report_lines.append(f"Keywords encontradas: {summary['keywords_found']}")
    report_lines.append(f"Keywords faltantes: {summary.get('keywords_missing', 0)}")
    report_lines.append(f"Precisión (Accuracy): {summary['accuracy']:.2%}")
    report_lines.append(f"Score promedio por prompt: {summary.get('average_score_per_prompt', 0.0):.2%}")
    report_lines.append("")
    
    # Sección de prompts con 0 keywords encontradas
    zero_keywords = summary['prompts_with_zero_keywords']
    report_lines.append("=" * 80)
    report_lines.append(f"PROMPTS CON CERO KEYWORDS ENCONTRADAS ({len(zero_keywords)}):")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    if len(zero_keywords) == 0:
        report_lines.append("✓ Todos los prompts encontraron al menos una keyword.")
        report_lines.append("")
    else:
        # Mostrar cada prompt que no encontró keywords
        for idx, item in enumerate(zero_keywords, 1):
            report_lines.append(f"Prompt #{idx} (Índice: {item.get('prompt_index', 'N/A')}):")
            prompt_text = item['prompt']
            if len(prompt_text) > 100:
                report_lines.append(f"  Prompt: {prompt_text[:100]}...")
            else:
                report_lines.append(f"  Prompt: {prompt_text}")
            response_text = item['response']
            if len(response_text) > 200:
                report_lines.append(f"  Response: {response_text[:200]}...")
            else:
                report_lines.append(f"  Response: {response_text}")
            report_lines.append(f"  Keywords esperadas: {', '.join(item['expected_keywords'])}")
            report_lines.append("")
    
    # Resultados detallados por prompt (opcional)
    if detailed:
        report_lines.append("=" * 80)
        report_lines.append("RESULTADOS DETALLADOS POR PROMPT:")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        for result in summary.get('per_prompt_results', []):
            report_lines.append(f"Prompt #{result.get('prompt_index', 'N/A') + 1}:")
            report_lines.append(f"  Score: {result['score']:.2%} ({result['found_count']}/{result['total_keywords']})")
            report_lines.append(f"  Keywords encontradas: {', '.join(result['found_keywords']) if result['found_keywords'] else 'Ninguna'}")
            if result['missing_keywords']:
                report_lines.append(f"  Keywords faltantes: {', '.join(result['missing_keywords'])}")
            report_lines.append("")
    
    # Pie de página
    report_lines.append("=" * 80)
    report_lines.append("Fin del reporte")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


def print_report(summary: Dict[str, Any], detailed: bool = False):
    """
    Imprime el reporte en consola.
    
    Args:
        summary: Diccionario de resumen retornado por evaluate_responses
        detailed: Si es True, incluye resultados detallados de cada prompt
    """
    report = generate_report(summary, detailed)
    print(report)


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de datos de prueba
    example_pairs = [
        {
            "prompt": "¿Qué es Python?",
            "response": "Python es un lenguaje de programación de alto nivel, interpretado y de propósito general.",
            "expected_keywords": ["Python", "lenguaje", "programación"]
        },
        {
            "prompt": "Explica machine learning",
            "response": "Machine learning es una rama de la inteligencia artificial.",
            "expected_keywords": ["machine", "learning", "inteligencia", "artificial", "algoritmo"]
        },
        {
            "prompt": "Describe un algoritmo",
            "response": "Un proceso paso a paso para resolver un problema.",
            "expected_keywords": ["algoritmo", "proceso", "problema"]
        },
        {
            "prompt": "¿Qué es la API?",
            "response": "Una interfaz de programación de aplicaciones.",
            "expected_keywords": ["API", "interfaz", "programación"]
        },
        {
            "prompt": "Explica blockchain",
            "response": "Es una tecnología de registro distribuido.",
            "expected_keywords": ["blockchain", "distribuido", "cadena", "bloques"]  # Este no encontrará todas
        }
    ]
    
    # Evaluar respuestas con diferentes configuraciones
    print("=" * 80)
    print("EVALUACIÓN DE RESPUESTAS - EJEMPLO")
    print("=" * 80)
    print()
    
    # Evaluación básica (búsqueda de substring)
    print("1. Evaluando con búsqueda de substring (default)...")
    summary = evaluate_responses(example_pairs, word_boundary=False, case_sensitive=False)
    print(f"   Accuracy: {summary['accuracy']:.2%}")
    print(f"   Score promedio: {summary['average_score_per_prompt']:.2%}")
    print()
    
    # Evaluación con palabras completas
    print("2. Evaluando con búsqueda de palabras completas...")
    summary_word = evaluate_responses(example_pairs, word_boundary=True, case_sensitive=False)
    print(f"   Accuracy: {summary_word['accuracy']:.2%}")
    print(f"   Score promedio: {summary_word['average_score_per_prompt']:.2%}")
    print()
    
    # Generar e imprimir reporte detallado
    print("=" * 80)
    print("REPORTE DETALLADO:")
    print("=" * 80)
    print()
    print_report(summary, detailed=True)
    
    # También se puede acceder directamente al summary dict
    print("\n" + "=" * 80)
    print("RESUMEN EN FORMATO DICT:")
    print("=" * 80)
    print(f"Total prompts: {summary['total_prompts']}")
    print(f"Total keywords: {summary['total_keywords']}")
    print(f"Keywords encontradas: {summary['keywords_found']}")
    print(f"Keywords faltantes: {summary['keywords_missing']}")
    print(f"Accuracy: {summary['accuracy']:.2%}")
    print(f"Score promedio: {summary['average_score_per_prompt']:.2%}")
    print(f"Prompts con 0 keywords: {len(summary['prompts_with_zero_keywords'])}")
    print(f"Total resultados detallados: {len(summary['per_prompt_results'])}")

