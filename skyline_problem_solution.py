"""
LeetCode 218: The Skyline Problem
==================================

Implementación del algoritmo para resolver el problema del skyline
usando el método de línea de barrido (sweep line) con priority queue.
"""

import heapq
from typing import List


def getSkyline(buildings: List[List[int]]) -> List[List[int]]:
    """
    Resuelve el problema del skyline.
    
    Args:
        buildings: Lista de edificios donde cada edificio es [left, right, height]
        
    Returns:
        Lista de puntos clave del skyline [[x1, y1], [x2, y2], ...]
        
    Ejemplo:
        >>> buildings = [[2,9,10], [3,7,15], [5,12,12]]
        >>> getSkyline(buildings)
        [[2, 10], [3, 15], [7, 12], [12, 0]]
    """
    if not buildings:
        return []
    
    # Paso 1: Crear eventos (inicio y fin de cada edificio)
    events = []
    for left, right, height in buildings:
        # Evento de inicio: (x, altura, tipo)
        events.append((left, height, 'start'))
        # Evento de fin: (x, altura, tipo)
        events.append((right, height, 'end'))
    
    # Paso 2: Ordenar eventos por coordenada X
    # Si hay empates:
    #   - Inicios: el más alto primero (para que se agregue primero)
    #   - Fines: el más bajo primero (para que se remueva primero)
    #   - Inicio antes que fin si tienen la misma X
    events.sort(key=lambda x: (
        x[0],  # Primero por X
        -x[1] if x[2] == 'start' else x[1]  # Luego por altura (negativa para start)
    ))
    
    # Paso 3: Procesar eventos
    # Usamos un max-heap (simulado con min-heap de valores negativos)
    heap = []  # Contiene alturas negativas (para simular max-heap)
    removed = {}  # Diccionario para lazy deletion
    result = []
    prev_height = 0  # Altura anterior del skyline
    
    for x, height, event_type in events:
        if event_type == 'start':
            # Agregar edificio al heap (usando negativo para max-heap)
            heapq.heappush(heap, -height)
        else:  # event_type == 'end'
            # Marcar para remover (lazy deletion)
            removed[-height] = removed.get(-height, 0) + 1
        
        # Limpiar el heap: remover elementos marcados para eliminar
        while heap and removed.get(heap[0], 0) > 0:
            removed[heap[0]] -= 1
            heapq.heappop(heap)
        
        # Obtener la altura máxima actual
        # Si el heap está vacío, altura es 0 (suelo)
        current_height = -heap[0] if heap else 0
        
        # Solo agregar punto si la altura cambió
        if current_height != prev_height:
            result.append([x, current_height])
            prev_height = current_height
    
    return result


def getSkylineVerbose(buildings: List[List[int]]) -> List[List[int]]:
    """
    Versión con prints para entender el proceso paso a paso.
    """
    if not buildings:
        return []
    
    print("=" * 60)
    print("PROCESAMIENTO DEL SKYLINE PROBLEM")
    print("=" * 60)
    print(f"\nEdificios de entrada: {buildings}\n")
    
    # Crear eventos
    events = []
    for i, (left, right, height) in enumerate(buildings):
        events.append((left, height, 'start', i+1))
        events.append((right, height, 'end', i+1))
        print(f"Edificio {i+1}: [{left}, {right}, {height}]")
    
    # Ordenar
    events.sort(key=lambda x: (
        x[0],
        -x[1] if x[2] == 'start' else x[1]
    ))
    
    print(f"\nEventos ordenados:")
    for x, h, t, idx in events:
        print(f"  X={x:3d}, Altura={h:3d}, Tipo={t:5s}, Edificio {idx}")
    
    # Procesar
    heap = []
    removed = {}
    result = []
    prev_height = 0
    
    print(f"\n{'X':>4} | {'Evento':<15} | {'Heap':<20} | {'Max':>4} | {'Cambió?':<8} | Resultado")
    print("-" * 80)
    
    for x, height, event_type, idx in events:
        if event_type == 'start':
            heapq.heappush(heap, -height)
            action = f"Start Ed.{idx}"
        else:
            removed[-height] = removed.get(-height, 0) + 1
            action = f"End Ed.{idx}"
        
        # Limpiar heap
        while heap and removed.get(heap[0], 0) > 0:
            removed[heap[0]] -= 1
            heapq.heappop(heap)
        
        current_height = -heap[0] if heap else 0
        heap_str = str([-h for h in heap[:3]]) + ("..." if len(heap) > 3 else "")
        changed = "Sí" if current_height != prev_height else "No"
        
        if current_height != prev_height:
            result.append([x, current_height])
            result_str = str(result)
            prev_height = current_height
        else:
            result_str = str(result)
        
        print(f"{x:4d} | {action:<15} | {heap_str:<20} | {current_height:4d} | {changed:<8} | {result_str}")
    
    print("=" * 60)
    print(f"\nResultado final: {result}")
    print("=" * 60)
    
    return result


# Casos de prueba
if __name__ == "__main__":
    # Caso de ejemplo del problema
    print("\n" + "="*60)
    print("CASO 1: Ejemplo básico")
    print("="*60)
    buildings1 = [[2, 9, 10], [3, 7, 15], [5, 12, 12]]
    result1 = getSkylineVerbose(buildings1)
    print(f"\n[OK] Resultado: {result1}")
    print(f"[OK] Esperado: [[2, 10], [3, 15], [7, 12], [12, 0]]")
    
    # Caso simple: un solo edificio
    print("\n\n" + "="*60)
    print("CASO 2: Un solo edificio")
    print("="*60)
    buildings2 = [[0, 2, 3]]
    result2 = getSkyline(buildings2)
    print(f"Edificios: {buildings2}")
    print(f"Resultado: {result2}")
    print(f"Esperado: [[0, 3], [2, 0]]")
    
    # Caso: edificios no solapados
    print("\n\n" + "="*60)
    print("CASO 3: Edificios no solapados")
    print("="*60)
    buildings3 = [[1, 3, 5], [5, 7, 8]]
    result3 = getSkyline(buildings3)
    print(f"Edificios: {buildings3}")
    print(f"Resultado: {result3}")
    print(f"Esperado: [[1, 5], [3, 0], [5, 8], [7, 0]]")
    
    # Caso: edificios completamente solapados
    print("\n\n" + "="*60)
    print("CASO 4: Edificios solapados (uno dentro de otro)")
    print("="*60)
    buildings4 = [[1, 5, 10], [2, 4, 15]]
    result4 = getSkyline(buildings4)
    print(f"Edificios: {buildings4}")
    print(f"Resultado: {result4}")
    print(f"Esperado: [[1, 10], [2, 15], [4, 10], [5, 0]]")

