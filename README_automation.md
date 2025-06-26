# Scripts de Automatización de Terminal

## Descripción

Estos scripts automatizan la ejecución de comandos en la terminal de Cursor/VSCode sin necesidad de apuntar manualmente el cursor.

## Archivos

### 1. `automation_script.py` (Versión Avanzada)
- **Funcionalidades:**
  - Detecta automáticamente la ventana de Cursor/VSCode
  - Enfoca la terminal automáticamente 
  - Hotkey para detener (Ctrl+Shift+Q)
  - Manejo robusto de errores
  - Contador de ciclos
  - Espera interrumpible

### 2. `simple_automation.py` (Versión Simplificada)
- **Funcionalidades:**
  - Versión más ligera del script original
  - Usa failsafe de pyautogui (mouse en esquina para parar)
  - Enfoque automático de terminal
  - Mejor feedback visual

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Para la versión simplificada solo necesitas:
```bash
pip install pyautogui
```

## Uso

### Versión Avanzada:
```bash
python automation_script.py
```

### Versión Simplificada:
```bash
python simple_automation.py
```

## Mejoras Implementadas

### ✅ Problemas Solucionados del Script Original:

1. **Enfoque Automático**: Ya no necesitas apuntar manualmente el cursor
2. **Detección de Ventana**: Busca automáticamente Cursor/VSCode
3. **Control de Parada**: Múltiples formas de detener el script
4. **Manejo de Errores**: Captura y maneja errores graciosamente
5. **Feedback Visual**: Muestra progreso y estado actual
6. **Código Modular**: Estructura orientada a objetos más mantenible

### ⚙️ Configuración de Comandos:

Puedes modificar los comandos editando la lista `commands` en cualquiera de los scripts:

```python
commands = [
    ("tu_comando_1", tiempo_espera_segundos),
    ("tu_comando_2", tiempo_espera_segundos),
    # ...
]
```

### 🛑 Formas de Detener:

**Versión Avanzada:**
- `Ctrl+Shift+Q`
- `Ctrl+C` en la consola
- Mover mouse a esquina superior izquierda

**Versión Simplificada:**
- Mover mouse a esquina superior izquierda
- `Ctrl+C` en la consola

## Notas Importantes

- Los scripts funcionan específicamente con Cursor y VSCode
- Asegúrate de que la terminal esté disponible en el editor
- Los tiempos de espera están en segundos
- El script usa `Ctrl+Shift+` ` para enfocar la terminal

## Dependencias

- `pyautogui`: Automatización de GUI
- `keyboard`: Manejo de hotkeys (solo versión avanzada)
- `psutil`: Información del sistema (solo versión avanzada)  
- `pywin32`: Interacción con ventanas de Windows (solo versión avanzada) 