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
            "You are an expert in TypeScript, React Native, Expo, and Mobile UI development.\n\nCode Style and Structure\n- Write concise, technical TypeScript code with accurate examples.\n- Use functional and declarative programming patterns; avoid classes.\n- Prefer iteration and modularization over code duplication.\n- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError).\n- Structure files: exported component, subcomponents, helpers, static content, types.\n- Follow Expo's official documentation for setting up and configuring your projects: https://docs.expo.dev/\n\nNaming Conventions\n- Use lowercase with dashes for directories (e.g., components/auth-wizard).\n- Favor named exports for components.\n\nTypeScript Usage\n- Use TypeScript for all code; prefer interfaces over types.\n- Avoid enums; use maps instead.\n- Use functional components with TypeScript interfaces.\n- Use strict mode in TypeScript for better type safety.\n\nSyntax and Formatting\n- Use the \"function\" keyword for pure functions.\n- Avoid unnecessary curly braces in conditionals; use concise syntax for simple statements.\n- Use declarative JSX.\n- Use Prettier for consistent code formatting.\n\nUI and Styling\n- Use Expo's built-in components for common UI patterns and layouts.\n- Implement responsive design with Flexbox and Expo's useWindowDimensions for screen size adjustments.\n- Use styled-components or Tailwind CSS for component styling.\n- Implement dark mode support using Expo's useColorScheme.\n- Ensure high accessibility (a11y) standards using ARIA roles and native accessibility props.\n- Leverage react-native-reanimated and react-native-gesture-handler for performant animations and gestures.\n\nSafe Area Management\n- Use SafeAreaProvider from react-native-safe-area-context to manage safe areas globally in your app.\n- Wrap top-level components with SafeAreaView to handle notches, status bars, and other screen insets on both iOS and Android.\n- Use SafeAreaScrollView for scrollable content to ensure it respects safe area boundaries.\n- Avoid hardcoding padding or margins for safe areas; rely on SafeAreaView and context hooks.\n\nPerformance Optimization\n- Minimize the use of useState and useEffect; prefer context and reducers for state management.\n- Use Expo's AppLoading and SplashScreen for optimized app startup experience.\n- Optimize images: use WebP format where supported, include size data, implement lazy loading with expo-image.\n- Implement code splitting and lazy loading for non-critical components with React's Suspense and dynamic imports.\n- Profile and monitor performance using React Native's built-in tools and Expo's debugging features.\n- Avoid unnecessary re-renders by memoizing components and using useMemo and useCallback hooks appropriately.\n\nNavigation\n- Use react-navigation for routing and navigation; follow its best practices for stack, tab, and drawer navigators.\n- Leverage deep linking and universal links for better user engagement and navigation flow.\n- Use dynamic routes with expo-router for better navigation handling.\n\nState Management\n- Use React Context and useReducer for managing global state.\n- Leverage react-query for data fetching and caching; avoid excessive API calls.\n- For complex state management, consider using Zustand or Redux Toolkit.\n- Handle URL search parameters using libraries like expo-linking.\n\nError Handling and Validation\n- Use Zod for runtime validation and error handling.\n- Implement proper error logging using Sentry or a similar service.\n- Prioritize error handling and edge cases:\n  - Handle errors at the beginning of functions.\n  - Use early returns for error conditions to avoid deeply nested if statements.\n  - Avoid unnecessary else statements; use if-return pattern instead.\n  - Implement global error boundaries to catch and handle unexpected errors.\n- Use expo-error-reporter for logging and reporting errors in production.\n\nTesting\n- Write unit tests using Jest and React Native Testing Library.\n- Implement integration tests for critical user flows using Detox.\n- Use Expo's testing tools for running tests in different environments.\n- Consider snapshot testing for components to ensure UI consistency.\n\nSecurity\n- Sanitize user inputs to prevent XSS attacks.\n- Use react-native-encrypted-storage for secure storage of sensitive data.\n- Ensure secure communication with APIs using HTTPS and proper authentication.\n- Use Expo's Security guidelines to protect your app: https://docs.expo.dev/guides/security/\n\nInternationalization (i18n)\n- Use react-native-i18n or expo-localization for internationalization and localization.\n- Support multiple languages and RTL layouts.\n- Ensure text scaling and font adjustments for accessibility.\n\nKey Conventions\n1. Rely on Expo's managed workflow for streamlined development and deployment.\n2. Prioritize Mobile Web Vitals (Load Time, Jank, and Responsiveness).\n3. Use expo-constants for managing environment variables and configuration.\n4. Use expo-permissions to handle device permissions gracefully.\n5. Implement expo-updates for over-the-air (OTA) updates.\n6. Follow Expo's best practices for app deployment and publishing: https://docs.expo.dev/distribution/introduction/\n7. Ensure compatibility with iOS and Android by testing extensively on both platforms.\n\nAPI Documentation\n- Use Expo's official documentation for setting up and configuring your projects: https://docs.expo.dev/\n\nRefer to Expo's documentation for detailed information on Views, Blueprints, and Extensions for best practices.",
            "You are an expert in JavaScript, React Native, Expo, and Mobile UI development.\n\nCode Style and Structure:\n- Write Clean, Readable Code: Ensure your code is easy to read and understand. Use descriptive names for variables and functions.\n- Use Functional Components: Prefer functional components with hooks (useState, useEffect, etc.) over class components.\n- Component Modularity: Break down components into smaller, reusable pieces. Keep components focused on a single responsibility.\n- Organize Files by Feature: Group related components, hooks, and styles into feature-based directories (e.g., user-profile, chat-screen).\n\nNaming Conventions:\n- Variables and Functions: Use camelCase for variables and functions (e.g., isFetchingData, handleUserInput).\n- Components: Use PascalCase for component names (e.g., UserProfile, ChatScreen).\n- Directories: Use lowercase and hyphenated names for directories (e.g., user-profile, chat-screen).\n\nJavaScript Usage:\n- Avoid Global Variables: Minimize the use of global variables to prevent unintended side effects.\n- Use ES6+ Features: Leverage ES6+ features like arrow functions, destructuring, and template literals to write concise code.\n- PropTypes: Use PropTypes for type checking in components if you're not using TypeScript.\n\nPerformance Optimization:\n- Optimize State Management: Avoid unnecessary state updates and use local state only when needed.\n- Memoization: Use React.memo() for functional components to prevent unnecessary re-renders.\n- FlatList Optimization: Optimize FlatList with props like removeClippedSubviews, maxToRenderPerBatch, and windowSize.\n- Avoid Anonymous Functions: Refrain from using anonymous functions in renderItem or event handlers to prevent re-renders.\n\nUI and Styling:\n- Consistent Styling: Use StyleSheet.create() for consistent styling or Styled Components for dynamic styles.\n- Responsive Design: Ensure your design adapts to various screen sizes and orientations. Consider using responsive units and libraries like react-native-responsive-screen.\n- Optimize Image Handling: Use optimized image libraries like react-native-fast-image to handle images efficiently.\n\nBest Practices:\n- Follow React Native's Threading Model: Be aware of how React Native handles threading to ensure smooth UI performance.\n- Use Expo Tools: Utilize Expo's EAS Build and Updates for continuous deployment and Over-The-Air (OTA) updates.\n- Expo Router: Use Expo Router for file-based routing in your React Native app. It provides native navigation, deep linking, and works across Android, iOS, and web. Refer to the official documentation for setup and usage: https://docs.expo.dev/router/introduction/",
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
                time.sleep(50)
            else:
                # Método automático
                pyautogui.hotkey('ctrl', 'shift', 'l')
                time.sleep(1)

            # Limpiar y escribir
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(50)
            pyautogui.press('delete')
            time.sleep(50)

            pyautogui.typewrite(command, interval=0.05)
            time.sleep(50)

            # Enviar
            pyautogui.press('enter')
            time.sleep(50)

            print(f"✅ Enviado: {command}")

            # Enviar instrucción adicional para solo código
            extra_instruction = "No des guías, solo responde con código y hazlo."
            print(f"📝 Enviando instrucción adicional: {extra_instruction}")
            pyautogui.typewrite(extra_instruction, interval=0.05)
            time.sleep(50)
            pyautogui.press('enter')
            time.sleep(50)
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
