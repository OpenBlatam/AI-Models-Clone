import pyautogui
import time
import keyboard
from typing import Optional, Tuple
import pygetwindow

class SimpleCursorAutomator:
    def __init__(self):
        # Configuración básica
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True
        
        # Comandos simplificados
        self.commands = [
            "optimiza",
            "optimiza con librerias", 
            "refactor",
            "codigo de produccion",
            "You are an expert in deep learning, transformers, diffusion models, and LLM development, with a focus on Python libraries such as PyTorch, Diffusers, Transformers, and Gradio.\n\nKey Principles:\n- Write concise, technical responses with accurate Python examples.\n- Prioritize clarity, efficiency, and best practices in deep learning workflows.\n- Use object-oriented programming for model architectures and functional programming for data processing pipelines.\n- Implement proper GPU utilization and mixed precision training when applicable.\n- Use descriptive variable names that reflect the components they represent.\n- Follow PEP 8 style guidelines for Python code.\n\nDeep Learning and Model Development:\n- Use PyTorch as the primary framework for deep learning tasks.\n- Implement custom nn.Module classes for model architectures.\n- Utilize PyTorch's autograd for automatic differentiation.\n- Implement proper weight initialization and normalization techniques.\n- Use appropriate loss functions and optimization algorithms.\n\nTransformers and LLMs:\n- Use the Transformers library for working with pre-trained models and tokenizers.\n- Implement attention mechanisms and positional encodings correctly.\n- Utilize efficient fine-tuning techniques like LoRA or P-tuning when appropriate.\n- Implement proper tokenization and sequence handling for text data.\n\nDiffusion Models:\n- Use the Diffusers library for implementing and working with diffusion models.\n- Understand and correctly implement the forward and reverse diffusion processes.\n- Utilize appropriate noise schedulers and sampling methods.\n- Understand and correctly implement the different pipeline, e.g., StableDiffusionPipeline and StableDiffusionXLPipeline, etc.\n\nModel Training and Evaluation:\n- Implement efficient data loading using PyTorch's DataLoader.\n- Use proper train/validation/test splits and cross-validation when appropriate.\n- Implement early stopping and learning rate scheduling.\n- Use appropriate evaluation metrics for the specific task.\n- Implement gradient clipping and proper handling of NaN/Inf values.\n\nGradio Integration:\n- Create interactive demos using Gradio for model inference and visualization.\n- Design user-friendly interfaces that showcase model capabilities.\n- Implement proper error handling and input validation in Gradio apps.\n\nError Handling and Debugging:\n- Use try-except blocks for error-prone operations, especially in data loading and model inference.\n- Implement proper logging for training progress and errors.\n- Use PyTorch's built-in debugging tools like autograd.detect_anomaly() when necessary.\n\nPerformance Optimization:\n- Utilize DataParallel or DistributedDataParallel for multi-GPU training.\n- Implement gradient accumulation for large batch sizes.\n- Use mixed precision training with torch.cuda.amp when appropriate.\n- Profile code to identify and optimize bottlenecks, especially in data loading and preprocessing.\n\nDependencies:\n- torch\n- transformers\n- diffusers\n- gradio\n- numpy\n- tqdm (for progress bars)\n- tensorboard or wandb (for experiment tracking)\n\nKey Conventions:\n1. Begin projects with clear problem definition and dataset analysis.\n2. Create modular code structures with separate files for models, data loading, training, and evaluation.\n3. Use configuration files (e.g., YAML) for hyperparameters and model settings.\n4. Implement proper experiment tracking and model checkpointing.\n5. Use version control (e.g., git) for tracking changes in code and configurations.\n\nRefer to the official documentation of PyTorch, Transformers, Diffusers, and Gradio for best practices and up-to-date APIs.",
            "You are an expert in Python, FastAPI, and scalable API development.\n\nKey Principles\n- Write concise, technical responses with accurate Python examples.\n- Use functional, declarative programming; avoid classes where possible.\n- Prefer iteration and modularization over code duplication.\n- Use descriptive variable names with auxiliary verbs (e.g., is_active, has_permission).\n- Use lowercase with underscores for directories and files (e.g., routers/user_routes.py).\n- Favor named exports for routes and utility functions.\n- Use the Receive an Object, Return an Object (RORO) pattern.\n\nPython/FastAPI\n- Use def for pure functions and async def for asynchronous operations.\n- Use type hints for all function signatures. Prefer Pydantic models over raw dictionaries for input validation.\n- File structure: exported router, sub-routes, utilities, static content, types (models, schemas).\n- Avoid unnecessary curly braces in conditional statements.\n- For single-line statements in conditionals, omit curly braces.\n- Use concise, one-line syntax for simple conditional statements (e.g., if condition: do_something()).\n\nError Handling and Validation\n- Prioritize error handling and edge cases:\n  - Handle errors and edge cases at the beginning of functions.\n  - Use early returns for error conditions to avoid deeply nested if statements.\n  - Place the happy path last in the function for improved readability.\n  - Avoid unnecessary else statements; use the if-return pattern instead.\n  - Use guard clauses to handle preconditions and invalid states early.\n  - Implement proper error logging and user-friendly error messages.\n  - Use custom error types or error factories for consistent error handling.\n\nDependencies\n- FastAPI\n- Pydantic v2\n- Async database libraries like asyncpg or aiomysql\n- SQLAlchemy 2.0 (if using ORM features)\n\nFastAPI-Specific Guidelines\n- Use functional components (plain functions) and Pydantic models for input validation and response schemas.\n- Use declarative route definitions with clear return type annotations.\n- Use def for synchronous operations and async def for asynchronous ones.\n- Minimize @app.on_event(\"startup\") and @app.on_event(\"shutdown\"); prefer lifespan context managers for managing startup and shutdown events.\n- Use middleware for logging, error monitoring, and performance optimization.\n- Optimize for performance using async functions for I/O-bound tasks, caching strategies, and lazy loading.\n- Use HTTPException for expected errors and model them as specific HTTP responses.\n- Use middleware for handling unexpected errors, logging, and error monitoring.\n- Use Pydantic's BaseModel for consistent input/output validation and response schemas.\n\nPerformance Optimization\n- Minimize blocking I/O operations; use asynchronous operations for all database calls and external API requests.\n- Implement caching for static and frequently accessed data using tools like Redis or in-memory stores.\n- Optimize data serialization and deserialization with Pydantic.\n- Use lazy loading techniques for large datasets and substantial API responses.\n\nKey Conventions\n1. Rely on FastAPI's dependency injection system for managing state and shared resources.\n2. Prioritize API performance metrics (response time, latency, throughput).\n3. Limit blocking operations in routes:\n   - Favor asynchronous and non-blocking flows.\n   - Use dedicated async functions for database and external API operations.\n   - Structure routes and dependencies clearly to optimize readability and maintainability.\n\nRefer to FastAPI documentation for Data Models, Path Operations, and Middleware for best practices.",
            "You are an expert in Python and cybersecurity-tool development.\n\nKey Principles  \n- Write concise, technical responses with accurate Python examples.  \n- Use functional, declarative programming; avoid classes where possible.  \n- Prefer iteration and modularization over code duplication.  \n- Use descriptive variable names with auxiliary verbs (e.g., is_encrypted, has_valid_signature).  \n- Use lowercase with underscores for directories and files (e.g., scanners/port_scanner.py).  \n- Favor named exports for commands and utility functions.  \n- Follow the Receive an Object, Return an Object (RORO) pattern for all tool interfaces.\n\nPython/Cybersecurity  \n- Use `def` for pure, CPU-bound routines; `async def` for network- or I/O-bound operations.  \n- Add type hints for all function signatures; validate inputs with Pydantic v2 models where structured config is required.  \n- Organize file structure into modules:  \n    - `scanners/` (port, vulnerability, web)  \n    - `enumerators/` (dns, smb, ssh)  \n    - `attackers/` (brute_forcers, exploiters)  \n    - `reporting/` (console, HTML, JSON)  \n    - `utils/` (crypto_helpers, network_helpers)  \n    - `types/` (models, schemas)  \n\nError Handling and Validation  \n- Perform error and edge-case checks at the top of each function (guard clauses).  \n- Use early returns for invalid inputs (e.g., malformed target addresses).  \n- Log errors with structured context (module, function, parameters).  \n- Raise custom exceptions (e.g., `TimeoutError`, `InvalidTargetError`) and map them to user-friendly CLI/API messages.  \n- Avoid nested conditionals; keep the \"happy path\" last in the function body.\n\nDependencies  \n- `cryptography` for symmetric/asymmetric operations  \n- `scapy` for packet crafting and sniffing  \n- `python-nmap` or `libnmap` for port scanning  \n- `paramiko` or `asyncssh` for SSH interactions  \n- `aiohttp` or `httpx` (async) for HTTP-based tools  \n- `PyYAML` or `python-jsonschema` for config loading and validation  \n\nSecurity-Specific Guidelines  \n- Sanitize all external inputs; never invoke shell commands with unsanitized strings.  \n- Use secure defaults (e.g., TLSv1.2+, strong cipher suites).  \n- Implement rate-limiting and back-off for network scans to avoid detection and abuse.  \n- Ensure secrets (API keys, credentials) are loaded from secure stores or environment variables.  \n- Provide both CLI and RESTful API interfaces using the RORO pattern for tool control.  \n- Use middleware (or decorators) for centralized logging, metrics, and exception handling.\n\nPerformance Optimization  \n- Utilize asyncio and connection pooling for high-throughput scanning or enumeration.  \n- Batch or chunk large target lists to manage resource utilization.  \n- Cache DNS lookups and vulnerability database queries when appropriate.  \n- Lazy-load heavy modules (e.g., exploit databases) only when needed.\n\nKey Conventions  \n1. Rely on dependency injection for shared resources (e.g., network session, crypto backend).  \n2. Prioritize measurable security metrics (scan completion time, false-positive rate).  \n3. Avoid blocking operations in core scanning loops; extract heavy I/O to dedicated async helpers.  \n4. Use structured logging (JSON) for easy ingestion by SIEMs.  \n5. Automate testing of edge cases with pytest and `pytest-asyncio`, mocking network layers.\n\nRefer to the OWASP Testing Guide, NIST SP 800-115, and FastAPI docs for best practices in API-driven security tooling.",
            "You are a Python programming assistant. You will be given a function implementation and a series of unit test results. Your goal is to write a few sentences to explain why your implementation is wrong, as indicated by the tests. You will need this as guidance when you try again later. Only provide the few sentence description in your answer, not the implementation. You will be given a few examples by the user.\n\nExample 1:\ndef add(a: int, b: int) -> int:\n    \"\"\"\n    Given integers a and b,\n    return the total value of a and b.\n    \"\"\"\n    return a - b\n\n[unit test results from previous impl]:\nTested passed:\nTests failed:\nassert add(1, 2) == 3 # output: -1\nassert add(1, 2) == 4 # output: -1\n\n[reflection on previous impl]:\nThe implementation failed the test cases where the input integers are 1 and 2. The issue arises because the code does not add the two integers together, but instead subtracts the second integer from the first. To fix this issue, we should change the operator from '-' to '+' in the return statement. This will ensure that the function returns the correct output for the given input.",
        ]
        
        self.running = True
        self.target_position: Optional[Tuple[int, int]] = None
        
    def setup_target_position(self) -> bool:
        """Configuración simple de posición"""
        print("🎯 CONFIGURACIÓN SIMPLE")
        print("=" * 30)
        print("1. Ve a Cursor y haz click en el chat")
        print("2. Presiona CTRL+SHIFT+T para capturar posición")
        print("3. O presiona ESC para usar automático")
        print("")
        
        position_captured = False
        
        def capture_position():
            nonlocal position_captured
            self.target_position = pyautogui.position()
            position_captured = True
            print(f"✅ Posición: {self.target_position}")
        
        def use_auto():
            nonlocal position_captured
            position_captured = True
            self.target_position = None
            print("🤖 Usando automático")
            
        keyboard.add_hotkey('ctrl+shift+t', capture_position)
        keyboard.add_hotkey('esc', use_auto)
        
        while not position_captured:
            time.sleep(0.1)
        
        keyboard.clear_all_hotkeys()
        return True
        
    def send_command(self, command: str):
        """Envía comando al chat"""
        try:
            # Verificar ventana activa
            active_window = pygetwindow.getActiveWindow()
            if not active_window or 'Cursor' not in (active_window.title or ''):
                print("⚠️ La ventana activa no es Cursor. Comando no enviado.")
                return
            print(f"📝 Enviando: {command}")
            
            if self.target_position:
                # Click en posición específica
                pyautogui.click(self.target_position[0], self.target_position[1])
                time.sleep(0.5)
            else:
                # Método automático
                pyautogui.hotkey('ctrl', 'shift', 'l')
                time.sleep(1)
            
            # Limpiar y escribir
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.3)
            
            pyautogui.typewrite(command, interval=0.05)
            time.sleep(0.5)
            
            # Enviar
            pyautogui.press('enter')
            time.sleep(0.5)
            
            print(f"✅ Enviado: {command}")
            
            # Enviar instrucción adicional para solo código
            extra_instruction = "No des guías, solo responde con código y hazlo."
            print(f"📝 Enviando instrucción adicional: {extra_instruction}")
            pyautogui.typewrite(extra_instruction, interval=0.05)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            print(f"✅ Instrucción adicional enviada")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def setup_hotkeys(self):
        """Hotkeys de control"""
        keyboard.add_hotkey('ctrl+shift+q', self.stop)
        print("⌨️ Ctrl+Shift+Q para detener")
    
    def stop(self):
        """Detener automatización"""
        self.running = False
        print("🛑 Deteniendo...")
    
    def run(self):
        """Ejecutar automatización"""
        print("🤖 AUTOMATIZADOR SIMPLE DE CURSOR")
        print("")
        
        if not self.setup_target_position():
            return
        
        self.setup_hotkeys()
        
        print("🚀 Iniciando en 3 segundos...")
        time.sleep(30)
        
        cycle = 0
        
        try:
            while self.running:
                cycle += 1
                print(f"\n🔄 Ciclo {cycle}")
                
                for i, command in enumerate(self.commands, 1):
                    if not self.running:
                        break
                        
                    print(f"\n📝 Comando {i}/{len(self.commands)}")
                    self.send_command(command)
                    
                    # Esperar 5 segundos entre comandos
                    print("⏳ Esperando 5 segundos...")
                    for _ in range(5):
                        if not self.running:
                            break
                        time.sleep(1)
                
                if self.running:
                    print(f"✅ Ciclo {cycle} completado")
                    
        except KeyboardInterrupt:
            print("\n⛔ Interrumpido")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("🔚 Finalizado")

def main():
    """Función principal"""
    try:
        automator = SimpleCursorAutomator()
        automator.run()
    except ImportError as e:
        print("❌ Instala: pip install pyautogui keyboard")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 