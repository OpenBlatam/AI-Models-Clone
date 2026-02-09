"""
LeetCode 42: Trapping Rain Water
=================================

Implementaciones del algoritmo para calcular agua atrapada entre barras.
Incluye múltiples enfoques: Two Pointers, Dynamic Programming, y Stack.
"""

from typing import List


def trap(height: List[int]) -> int:
    """
    Solución óptima usando Two Pointers.
    
    Complejidad: O(n) tiempo, O(1) espacio
    
    Args:
        height: Lista de alturas de las barras
        
    Returns:
        Total de unidades de agua atrapada
        
    Example:
        >>> trap([0,1,0,2,1,0,1,3,2,1,2,1])
        6
        >>> trap([4,2,0,3,2,5])
        9
    """
    # Caso base: necesitamos al menos 3 barras para atrapar agua
    if not height or len(height) < 3:
        return 0
    
    # Inicializar punteros en los extremos
    left = 0
    right = len(height) - 1
    
    # Máximos locales desde cada extremo
    left_max = 0  # Máximo encontrado desde la izquierda
    right_max = 0  # Máximo encontrado desde la derecha
    
    # Contador de agua atrapada
    water = 0
    
    # Mover punteros hasta que se encuentren
    while left < right:
        # Si la barra izquierda es más baja
        if height[left] < height[right]:
            # Si la barra actual es más alta que el máximo izquierdo
            if height[left] >= left_max:
                # Actualizar máximo izquierdo
                left_max = height[left]
            else:
                # Hay agua atrapada: máximo - altura actual
                water += left_max - height[left]
            # Avanzar puntero izquierdo
            left += 1
        else:
            # La barra derecha es más baja o igual
            if height[right] >= right_max:
                # Actualizar máximo derecho
                right_max = height[right]
            else:
                # Hay agua atrapada: máximo - altura actual
                water += right_max - height[right]
            # Retroceder puntero derecho
            right -= 1
    
    return water


def trap_dp(height: List[int]) -> int:
    """
    Solución usando Dynamic Programming.
    
    Complejidad: O(n) tiempo, O(n) espacio
    
    Estrategia:
    1. Pre-calcular máximos a la izquierda para cada posición
    2. Pre-calcular máximos a la derecha para cada posición
    3. Para cada posición, calcular agua = min(left_max, right_max) - height[i]
    """
    if not height or len(height) < 3:
        return 0
    
    n = len(height)
    
    # Pre-calcular máximos a la izquierda
    left_max = [0] * n
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i-1], height[i])
    
    # Pre-calcular máximos a la derecha
    right_max = [0] * n
    right_max[n-1] = height[n-1]
    for i in range(n-2, -1, -1):
        right_max[i] = max(right_max[i+1], height[i])
    
    # Calcular agua atrapada
    water = 0
    for i in range(n):
        water += min(left_max[i], right_max[i]) - height[i]
    
    return water


def trap_stack(height: List[int]) -> int:
    """
    Solución usando Stack.
    
    Complejidad: O(n) tiempo, O(n) espacio
    
    Estrategia:
    Usa un stack para mantener índices de barras en orden decreciente.
    Cuando encontramos una barra más alta, calculamos el agua atrapada.
    """
    if not height or len(height) < 3:
        return 0
    
    stack = []
    water = 0
    
    for i in range(len(height)):
        # Mientras haya barras en el stack y la actual sea más alta
        while stack and height[i] > height[stack[-1]]:
            # Barrera inferior (donde se acumula el agua)
            top = stack.pop()
            
            # Si no hay barrera izquierda, no se puede atrapar agua
            if not stack:
                break
            
            # Calcular dimensiones del contenedor
            distance = i - stack[-1] - 1
            bounded_height = min(height[i], height[stack[-1]]) - height[top]
            
            # Agregar agua atrapada
            water += distance * bounded_height
        
        # Agregar índice actual al stack
        stack.append(i)
    
    return water


def trap_verbose(height: List[int]) -> int:
    """
    Versión con prints para entender el proceso paso a paso.
    """
    if not height or len(height) < 3:
        return 0
    
    left = 0
    right = len(height) - 1
    left_max = 0
    right_max = 0
    water = 0
    
    print("=" * 80)
    print("PROCESAMIENTO DE TRAPPING RAIN WATER")
    print("=" * 80)
    print(f"\nAlturas: {height}\n")
    print(f"{'Iter':<5} | {'left':<5} | {'right':<6} | {'h[left]':<8} | {'h[right]':<9} | "
          f"{'left_max':<9} | {'right_max':<10} | {'water':<6} | Acción")
    print("-" * 100)
    
    iteration = 0
    while left < right:
        iteration += 1
        action = ""
        h_left_val = height[left]
        h_right_val = height[right]
        
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
                action = f"Actualizar left_max = {left_max}"
            else:
                added = left_max - height[left]
                water += added
                action = f"Agregar agua: {added} (total: {water})"
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
                action = f"Actualizar right_max = {right_max}"
            else:
                added = right_max - height[right]
                water += added
                action = f"Agregar agua: {added} (total: {water})"
            right -= 1
        
        print(f"{iteration:<5} | {left:<5} | {right:<6} | {h_left_val:<8} | "
              f"{h_right_val:<9} | "
              f"{left_max:<9} | {right_max:<10} | {water:<6} | {action}")
    
    print("=" * 100)
    print(f"\nResultado final: {water} unidades de agua")
    print("=" * 80)
    
    return water


def visualize_trapping(height: List[int]) -> None:
    """
    Visualiza el agua atrapada en ASCII.
    """
    if not height:
        return
    
    max_height = max(height) if height else 0
    water = trap(height)
    
    print("\n" + "=" * 60)
    print("VISUALIZACIÓN DEL AGUA ATRAPADA")
    print("=" * 60)
    print(f"Alturas: {height}")
    print(f"Agua atrapada: {water} unidades\n")
    
    # Calcular agua en cada posición
    water_levels = []
    if len(height) >= 3:
        left_max = [0] * len(height)
        right_max = [0] * len(height)
        
        left_max[0] = height[0]
        for i in range(1, len(height)):
            left_max[i] = max(left_max[i-1], height[i])
        
        right_max[len(height)-1] = height[len(height)-1]
        for i in range(len(height)-2, -1, -1):
            right_max[i] = max(right_max[i+1], height[i])
        
        for i in range(len(height)):
            water_level = min(left_max[i], right_max[i]) - height[i]
            water_levels.append(water_level)
    else:
        water_levels = [0] * len(height)
    
    # Dibujar desde arriba hacia abajo
    for level in range(max_height, -1, -1):
        line = ""
        for i, h in enumerate(height):
            if h > level:
                line += "# "  # Barra
            elif level < h + water_levels[i]:
                line += "~ "  # Agua
            else:
                line += "  "  # Vacío
        print(line)
    
    # Eje X
    print("-" * (len(height) * 2))
    indices = " ".join(str(i % 10) for i in range(len(height)))
    print(indices)
    print()


# Casos de prueba
if __name__ == "__main__":
    print("\n" + "="*80)
    print("CASO 1: Ejemplo básico de LeetCode")
    print("="*80)
    height1 = [0,1,0,2,1,0,1,3,2,1,2,1]
    result1 = trap(height1)
    print(f"Input: {height1}")
    print(f"Output: {result1}")
    print(f"Esperado: 6")
    visualize_trapping(height1)
    
    print("\n" + "="*80)
    print("CASO 2: Segundo ejemplo de LeetCode")
    print("="*80)
    height2 = [4,2,0,3,2,5]
    result2 = trap(height2)
    print(f"Input: {height2}")
    print(f"Output: {result2}")
    print(f"Esperado: 9")
    visualize_trapping(height2)
    
    print("\n" + "="*80)
    print("CASO 3: Versión verbose del primer ejemplo")
    print("="*80)
    trap_verbose([0,1,0,2,1,0,1,3,2,1,2,1])
    
    print("\n" + "="*80)
    print("CASO 4: Casos edge")
    print("="*80)
    
    # Array vacío
    assert trap([]) == 0, "Array vacío debe retornar 0"
    print("[OK] Array vacío: 0")
    
    # Menos de 3 elementos
    assert trap([1, 2]) == 0, "Menos de 3 elementos debe retornar 0"
    print("[OK] Menos de 3 elementos: 0")
    
    # Todas iguales
    assert trap([2, 2, 2, 2]) == 0, "Todas iguales debe retornar 0"
    print("[OK] Todas iguales: 0")
    
    # Creciente
    assert trap([1, 2, 3, 4, 5]) == 0, "Creciente debe retornar 0"
    print("[OK] Creciente: 0")
    
    # Decreciente
    assert trap([5, 4, 3, 2, 1]) == 0, "Decreciente debe retornar 0"
    print("[OK] Decreciente: 0")
    
    # Múltiples picos
    result3 = trap([3, 0, 2, 0, 4])
    assert result3 == 7, f"Múltiples picos debe retornar 7, obtuvo {result3}"
    print(f"[OK] Múltiples picos: {result3}")
    visualize_trapping([3, 0, 2, 0, 4])
    
    print("\n" + "="*80)
    print("COMPARACIÓN DE ENFOQUES")
    print("="*80)
    test_cases = [
        [0,1,0,2,1,0,1,3,2,1,2,1],
        [4,2,0,3,2,5],
        [3, 0, 2, 0, 4],
    ]
    
    for heights in test_cases:
        result_tp = trap(heights)
        result_dp = trap_dp(heights)
        result_stack = trap_stack(heights)
        
        print(f"\nInput: {heights}")
        print(f"Two Pointers: {result_tp}")
        print(f"Dynamic Programming: {result_dp}")
        print(f"Stack: {result_stack}")
        
        assert result_tp == result_dp == result_stack, "Todos los métodos deben dar el mismo resultado"
        print("[OK] Todos los métodos coinciden")
    
    print("\n" + "="*80)
    print("[OK] TODOS LOS TESTS PASARON")
    print("="*80)

