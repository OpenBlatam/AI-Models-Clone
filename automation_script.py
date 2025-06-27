import pyautogui
import time
import keyboard
import psutil
import win32gui
import win32con
from typing import Optional, Tuple

class CursorChatAutomator:
    def __init__(self):
        # Configuración de pyautogui
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True  # Mover mouse a esquina superior izquierda para parar
        
        # Comandos a ejecutar en secuencia
        self.commands = [
            {"text": "optimiza", "wait": 300},
            {"text": "optimiza con librerias", "wait": 300}, 
            {"text": "refactor", "wait": 300},
            {"text": "codigo de produccion", "wait": 300}
        ]
        
        self.running = True
        self.target_position: Optional[Tuple[int, int]] = None
        
    def setup_target_position(self) -> bool:
        """Permite al usuario seleccionar manualmente dónde enviar los comandos"""
        print("🎯 CONFIGURACIÓN DE POSICIÓN OBJETIVO")
        print("=" * 50)
        print("1. Ve a la ventana de Cursor donde quieres que aparezcan los comandos")
        print("2. Haz click exactamente en el área de texto del chat donde escribes")
        print("3. Luego presiona CTRL+SHIFT+T para capturar esa posición")
        print("4. O presiona ESC para usar detección automática")
        print("")
        print("Esperando que selecciones la posición...")
        
        # Configurar hotkey temporal para capturar posición
        position_captured = False
        
        def capture_position():
            nonlocal position_captured
            self.target_position = pyautogui.position()
            position_captured = True
            print(f"✅ Posición capturada: {self.target_position}")
        
        def use_auto_detection():
            nonlocal position_captured
            position_captured = True
            self.target_position = None
            print("🤖 Usando detección automática")
            
        # Configurar hotkeys temporales
        keyboard.add_hotkey('ctrl+shift+t', capture_position)
        keyboard.add_hotkey('esc', use_auto_detection)
        
        # Esperar hasta que se capture la posición
        while not position_captured:
            time.sleep(0.1)
        
        # Limpiar hotkeys temporales
        keyboard.clear_all_hotkeys()
        
        return True
        
    def find_cursor_window(self) -> Optional[int]:
        """Busca la ventana de Cursor/VSCode y la enfoca"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if any(keyword in window_title.lower() for keyword in ['cursor', 'visual studio code', 'vscode']):
                    windows.append((hwnd, window_title))
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            # Tomar la primera ventana encontrada
            hwnd, title = windows[0]
            print(f"🔍 Encontrada ventana: {title}")
            
            # Enfocar la ventana con métodos múltiples
            try:
                # Restaurar ventana si está minimizada
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)
                
                # Traer al frente
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                
                # Activar la ventana
                win32gui.SetActiveWindow(hwnd)
                time.sleep(1)
                
                print(f"✅ Ventana enfocada: {title}")
                
            except Exception as e:
                print(f"⚠️ Error enfocando ventana: {e}")
                
            time.sleep(1)  # Dar tiempo extra para que se enfoque
            return hwnd
        
        return None
    
    def send_command_to_chat(self, command: str):
        """Envía un comando al área específica seleccionada"""
        try:
            print(f"🎯 Enviando comando: {command}")
            
            # Enfocar ventana primero
            self.find_cursor_window()
            time.sleep(1)
            
            if self.target_position:
                # Usar posición específica seleccionada por el usuario
                print(f"📍 Haciendo click en posición seleccionada: {self.target_position}")
                pyautogui.click(self.target_position[0], self.target_position[1])
                time.sleep(1)
            else:
                # Método automático de backup
                print("🤖 Usando método automático...")
                pyautogui.hotkey('ctrl', 'shift', 'l')  # Chat de IA
                time.sleep(2)
                pyautogui.hotkey('ctrl', 'i')  # Chat inline
                time.sleep(1)
            
            # Limpiar área de texto
            print("🧹 Limpiando texto...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.press('delete')
            time.sleep(0.5)
            
            # Escribir comando
            print(f"✍️ Escribiendo: {command}")
            pyautogui.typewrite(command, interval=0.1)
            time.sleep(1.5)  # Más tiempo para asegurar que se escriba completo
            
            # Enviar comando con Enter - múltiples intentos para asegurar
            print("📤 Presionando ENTER para enviar comando...")
            pyautogui.press('enter')
            time.sleep(0.5)
            
            # Segundo intento por si acaso
            pyautogui.press('enter')
            time.sleep(1)
            
            print(f"✅ COMANDO ENVIADO CON ENTER: {command}")
            print("📨 Mensaje enviado al chat de IA")
            
        except Exception as e:
            print(f"❌ Error enviando comando '{command}': {e}")
    
    def setup_hotkeys(self):
        """Configura hotkeys para controlar el script"""
        keyboard.add_hotkey('ctrl+shift+q', self.stop_automation)
        print("⌨️ Hotkey configurado: Ctrl+Shift+Q para detener")
    
    def stop_automation(self):
        """Detiene la automatización"""
        self.running = False
        print("🛑 Deteniendo automatización...")
    
    def run(self):
        """Ejecuta el bucle principal de automatización"""
        print("🤖 === AUTOMATIZADOR INTELIGENTE DE CURSOR ===")
        print("")
        
        # Paso 1: Configurar posición objetivo
        if not self.setup_target_position():
            return
        
        print("")
        print("🔍 Buscando ventana de Cursor...")
        
        # Configurar hotkeys
        self.setup_hotkeys()
        
        # Buscar y enfocar ventana de Cursor
        if not self.find_cursor_window():
            print("❌ No se encontró ventana de Cursor/VSCode abierta")
            print("Por favor abre Cursor y ejecuta el script nuevamente")
            return
        
        print("")
        print("🚀 Iniciando automatización en 3 segundos...")
        print("⌨️ Presiona Ctrl+Shift+Q para detener en cualquier momento")
        time.sleep(3)
        
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                print(f"\n🔄 --- Ciclo {cycle_count} ---")
                
                for i, cmd_info in enumerate(self.commands, 1):
                    if not self.running:
                        break
                        
                    print(f"\n📝 Comando {i}/{len(self.commands)}")
                    
                    # Enviar comando al chat
                    self.send_command_to_chat(cmd_info["text"])
                    
                    # Esperar el tiempo especificado
                    wait_time = cmd_info["wait"]
                    print(f"⏳ Esperando {wait_time} segundos...")
                    
                    # Espera interrumpible
                    for _ in range(wait_time):
                        if not self.running:
                            break
                        time.sleep(1)
                
                if self.running:
                    print(f"✅ Ciclo {cycle_count} completado")
                    
        except KeyboardInterrupt:
            print("\n⛔ Interrupción manual detectada")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        finally:
            print("🔚 Automatización finalizada")

def main():
    """Función principal"""
    try:
        automator = CursorChatAutomator()
        automator.run()
    except ImportError as e:
        print("❌ Error: Faltan dependencias")
        print("Instala las dependencias con:")
        print("pip install pyautogui keyboard psutil pywin32")
    except Exception as e:
        print(f"❌ Error iniciando automatizador: {e}")

if __name__ == "__main__":
    main() 