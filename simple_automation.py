import pyautogui
import time
import sys

def setup_pyautogui():
    """Configuración inicial de pyautogui"""
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = True  # Mover mouse a esquina superior izquierda para parar
    print("Configuración: Mueve el mouse a la esquina superior izquierda para parar")

def send_command(command: str, wait_seconds: int = 0):
    """Envía un comando a la terminal activa"""
    try:
        # Enfocar terminal (funciona en VSCode/Cursor)
        pyautogui.hotkey('ctrl', 'shift', '`')
        time.sleep(0.5)
        
        # Escribir comando
        pyautogui.typewrite(command, interval=0.02)
        pyautogui.press('enter')
        print(f"✓ Comando enviado: '{command}'")
        
        # Esperar si se especifica
        if wait_seconds > 0:
            print(f"  Esperando {wait_seconds} segundos...")
            time.sleep(wait_seconds)
            
    except pyautogui.FailSafeException:
        print("Script detenido por failsafe (mouse en esquina)")
        sys.exit(0)
    except KeyboardInterrupt:
        print("Script detenido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error enviando comando '{command}': {e}")

def main():
    """Función principal - versión simplificada del script original"""
    
    # Configurar pyautogui
    setup_pyautogui()
    
    # Comandos a ejecutar (optimizados para mejor rendimiento)
    commands = [
        ("optimiza", 300),                    # 5 minutos (optimizado)
        ("optimiza con librerias", 350),      # 5.8 minutos (optimizado)  
        ("refactor", 400),                    # 6.7 minutos (optimizado)
        ("codigo de produccion", 45),         # 45 segundos (optimizado)
        ("test", 30),                        # 30 segundos (nuevo comando)
        ("build", 60)                        # 1 minuto (nuevo comando)
    ]
    
    print("=== AUTOMATIZACIÓN DE TERMINAL ===")
    print("Asegúrate de que Cursor/VSCode esté abierto")
    print("El script enviará comandos automáticamente a la terminal")
    print("\nComandos configurados:")
    for i, (cmd, wait) in enumerate(commands, 1):
        print(f"  {i}. '{cmd}' (espera {wait}s)")
    
    print(f"\nIniciando en 5 segundos...")
    print("Para detener: mueve el mouse a la esquina superior izquierda")
    time.sleep(5)
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            print(f"\n--- CICLO {cycle} ---")
            
            for i, (command, wait_time) in enumerate(commands, 1):
                print(f"\nComando {i}/{len(commands)}:")
                send_command(command, wait_time)
            
            print(f"Ciclo {cycle} completado. Iniciando siguiente ciclo...")
            
    except KeyboardInterrupt:
        print("\nScript detenido")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main() 