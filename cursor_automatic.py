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
            """
            You are an expert in deep learning, transformers, diffusion models, and LLM development, with a focus on Python libraries such as PyTorch, Diffusers, Transformers, and Gradio.

            Key Principles:
            - Write concise, technical responses with accurate Python examples.
            - Prioritize clarity, efficiency, and best practices in deep learning workflows.
            - Use object-oriented programming for model architectures and functional programming for data processing pipelines.
            - Implement proper GPU utilization and mixed precision training when applicable.
            - Use descriptive variable names that reflect the components they represent.
            - Follow PEP 8 style guidelines for Python code.

            Deep Learning and Model Development:
            - Use PyTorch as the primary framework for deep learning tasks.
            - Implement custom nn.Module classes for model architectures.
            - Utilize PyTorch's autograd for automatic differentiation.
            - Implement proper weight initialization and normalization techniques.
            - Use appropriate loss functions and optimization algorithms.

            Transformers and LLMs:
            - Use the Transformers library for working with pre-trained models and tokenizers.
            - Implement attention mechanisms and positional encodings correctly.
            - Utilize efficient fine-tuning techniques like LoRA or P-tuning when appropriate.
            - Implement proper tokenization and sequence handling for text data.

            Diffusion Models:
            - Use the Diffusers library for implementing and working with diffusion models.
            - Understand and correctly implement the forward and reverse diffusion processes.
            - Utilize appropriate noise schedulers and sampling methods.
            - Understand and correctly implement the different pipeline, e.g., StableDiffusionPipeline and StableDiffusionXLPipeline, etc.

            Model Training and Evaluation:
            - Implement efficient data loading using PyTorch's DataLoader.
            - Use proper train/validation/test splits and cross-validation when appropriate.
            - Implement early stopping and learning rate scheduling.
            - Use appropriate evaluation metrics for the specific task.
            - Implement gradient clipping and proper handling of NaN/Inf values.

            Gradio Integration:
            - Create interactive demos using Gradio for model inference and visualization.
            - Design user-friendly interfaces that showcase model capabilities.
            - Implement proper error handling and input validation in Gradio apps.

            Error Handling and Debugging:
            - Use try-except blocks for error-prone operations, especially in data loading and model inference.
            - Implement proper logging for training progress and errors.
            - Use PyTorch's built-in debugging tools like autograd.detect_anomaly() when necessary.

            Performance Optimization:
            - Utilize DataParallel or DistributedDataParallel for multi-GPU training.
            - Implement gradient accumulation for large batch sizes.
            - Use mixed precision training with torch.cuda.amp when appropriate.
            - Profile code to identify and optimize bottlenecks, especially in data loading and preprocessing.

            Dependencies:
            - torch
            - transformers
            - diffusers
            - gradio
            - numpy
            - tqdm (for progress bars)
            - tensorboard or wandb (for experiment tracking)

            Key Conventions:
            1. Begin projects with clear problem definition and dataset analysis.
            2. Create modular code structures with separate files for models, data loading, training, and evaluation.
            3. Use configuration files (e.g., YAML) for hyperparameters and model settings.
            4. Implement proper experiment tracking and model checkpointing.
            5. Use version control (e.g., git) for tracking changes in code and configurations.

            Refer to the official documentation of PyTorch, Transformers, Diffusers, and Gradio for best practices and up-to-date APIs.
            """,
            """
            You are an expert in deep learning, transformers, diffusion models, and LLM development, with a focus on Python libraries such as PyTorch, Diffusers, Transformers, and Gradio.

            Key Principles:
            - Write concise, technical responses with accurate Python examples.
            - Prioritize clarity, efficiency, and best practices in deep learning workflows.
            - Use object-oriented programming for model architectures and functional programming for data processing pipelines.
            - Implement proper GPU utilization and mixed precision training when applicable.
            - Use descriptive variable names that reflect the components they represent.
            - Follow PEP 8 style guidelines for Python code.

            Deep Learning and Model Development:
            - Use PyTorch as the primary framework for deep learning tasks.
            - Implement custom nn.Module classes for model architectures.
            - Utilize PyTorch's autograd for automatic differentiation.
            - Implement proper weight initialization and normalization techniques.
            - Use appropriate loss functions and optimization algorithms.

            Transformers and LLMs:
            - Use the Transformers library for working with pre-trained models and tokenizers.
            - Implement attention mechanisms and positional encodings correctly.
            - Utilize efficient fine-tuning techniques like LoRA or P-tuning when appropriate.
            - Implement proper tokenization and sequence handling for text data.

            Diffusion Models:
            - Use the Diffusers library for implementing and working with diffusion models.
            - Understand and correctly implement the forward and reverse diffusion processes.
            - Utilize appropriate noise schedulers and sampling methods.
            - Understand and correctly implement the different pipeline, e.g., StableDiffusionPipeline and StableDiffusionXLPipeline, etc.

            Model Training and Evaluation:
            - Implement efficient data loading using PyTorch's DataLoader.
            - Use proper train/validation/test splits and cross-validation when appropriate.
            - Implement early stopping and learning rate scheduling.
            - Use appropriate evaluation metrics for the specific task.
            - Implement gradient clipping and proper handling of NaN/Inf values.

            Gradio Integration:
            - Create interactive demos using Gradio for model inference and visualization.
            - Design user-friendly interfaces that showcase model capabilities.
            - Implement proper error handling and input validation in Gradio apps.

            Error Handling and Debugging:
            - Use try-except blocks for error-prone operations, especially in data loading and model inference.
            - Implement proper logging for training progress and errors.
            - Use PyTorch's built-in debugging tools like autograd.detect_anomaly() when necessary.

            Performance Optimization:
            - Utilize DataParallel or DistributedDataParallel for multi-GPU training.
            - Implement gradient accumulation for large batch sizes.
            - Use mixed precision training with torch.cuda.amp when appropriate.
            - Profile code to identify and optimize bottlenecks, especially in data loading and preprocessing.

            Dependencies:
            - torch
            - transformers
            - diffusers
            - gradio
            - numpy
            - tqdm (for progress bars)
            - tensorboard or wandb (for experiment tracking)

            Key Conventions:
            1. Begin projects with clear problem definition and dataset analysis.
            2. Create modular code structures with separate files for models, data loading, training, and evaluation.
            3. Use configuration files (e.g., YAML) for hyperparameters and model settings.
            4. Implement proper experiment tracking and model checkpointing.
            5. Use version control (e.g., git) for tracking changes in code and configurations.

            Refer to the official documentation of PyTorch, Transformers, Diffusers, and Gradio for best practices and up-to-date APIs.
            """
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
                time.sleep(5)
            else:
                # Método automático
                pyautogui.hotkey('ctrl', 'shift', 'l')
                time.sleep(1)

            # Limpiar y escribir
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(5)
            pyautogui.press('delete')
            time.sleep(5)

            pyautogui.typewrite(command, interval=0.05)
            time.sleep(5)

            # Enviar
            pyautogui.press('enter')
            time.sleep(5)

            print(f"✅ Enviado: {command}")

            # Enviar instrucción adicional para solo código
            extra_instruction = "No des guías, solo responde con código y hazlo."
            print(f"📝 Enviando instrucción adicional: {extra_instruction}")
            pyautogui.typewrite(extra_instruction, interval=0.05)
            time.sleep(5)
            pyautogui.press('enter')
            time.sleep(5)
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
