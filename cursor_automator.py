#!/usr/bin/env python3
"""
Simple Cursor Chat Automator

Features
- Window targeting by title (default: "Cursor")
- Optional mouse position capture via hotkey (default: Ctrl+Shift+T), or automatic chat focus
- Safe, configurable delays (no excessive waits)
- Global stop hotkey (Ctrl+Shift+Q)
- Configurable commands list via CLI or defaults

Usage
  py -3 cursor_automator.py --help
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import List, Optional, Tuple


def try_imports():
    try:
        import pyautogui  # type: ignore
        import keyboard  # type: ignore
        import pygetwindow  # type: ignore
        return pyautogui, keyboard, pygetwindow
    except Exception as exc:  # pragma: no cover
        print("❌ Missing or incompatible dependencies.")
        print("   Install with: pip install pyautogui keyboard pygetwindow")
        print(f"   Details: {exc}")
        sys.exit(1)


class SimpleCursorAutomator:
    def __init__(
        self,
        window_title: str = "Cursor",
        pause_seconds: float = 0.15,
        key_delay_seconds: float = 0.05,
        between_commands_seconds: float = 5.0,
        capture_hotkey: str = "ctrl+shift+t",
        stop_hotkey: str = "ctrl+shift+q",
        commands: Optional[List[str]] = None,
    ) -> None:
        self.pyautogui, self.keyboard, self.pygetwindow = try_imports()

        self.window_title = window_title
        self.pause_seconds = pause_seconds
        self.key_delay_seconds = key_delay_seconds
        self.between_commands_seconds = between_commands_seconds
        self.capture_hotkey = capture_hotkey
        self.stop_hotkey = stop_hotkey

        self.pyautogui.PAUSE = pause_seconds
        self.pyautogui.FAILSAFE = True

        self.running: bool = True
        self.target_position: Optional[Tuple[int, int]] = None

        self.commands = commands or [
            "optimiza",
            "optimiza con librerias",
            "refactor",
            "codigo de produccion",
            (
                "You are an expert in TypeScript, React Native, Expo, and Mobile UI development.\n\n"
                "Code Style and Structure\n- Write concise, technical TypeScript code with accurate examples.\n"
                "- Use functional and declarative programming patterns; avoid classes.\n"
                "- Prefer iteration and modularization over code duplication.\n"
                "- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError).\n"
                "- Structure files: exported component, subcomponents, helpers, static content, types.\n"
                "- Follow Expo's official documentation: https://docs.expo.dev/\n\n"
                "Naming Conventions\n- Use lowercase with dashes for directories (e.g., components/auth-wizard).\n"
                "- Favor named exports for components.\n\n"
                "TypeScript Usage\n- Use TypeScript; prefer interfaces over types.\n- Avoid enums; use maps.\n"
                "- Use functional components with interfaces.\n- Use strict mode.\n\n"
                "Syntax and Formatting\n- Use the 'function' keyword for pure functions.\n"
                "- Avoid unnecessary braces in conditionals.\n- Use declarative JSX.\n- Use Prettier.\n\n"
                "UI and Styling\n- Use Expo components.\n- Responsive design with Flexbox and useWindowDimensions.\n"
                "- styled-components or Tailwind.\n- Dark mode with useColorScheme.\n- High accessibility.\n"
                "- Use reanimated and gesture-handler for animations.\n\n"
                "Safe Area Management\n- SafeAreaProvider globally.\n- SafeAreaView at top-level.\n"
                "- SafeAreaScrollView for scroll content.\n- Avoid hardcoded insets.\n\n"
                "Performance Optimization\n- Minimize useState/useEffect; prefer reducers/context.\n"
                "- Use SplashScreen/AppLoading.\n- Optimize images.\n- Lazy load with Suspense.\n\n"
                "Navigation\n- react-navigation best practices.\n- Deep linking.\n- expo-router for file-based routing.\n\n"
                "State Management\n- Context + useReducer.\n- react-query.\n- Consider Zustand/RTK for complex cases.\n\n"
                "Error Handling and Validation\n- Zod for runtime validation.\n- Sentry.\n- Early returns.\n\n"
                "Testing\n- Jest + RNTL.\n- Detox for critical flows.\n- Snapshots if useful.\n\n"
                "Security\n- Sanitize inputs.\n- encrypted-storage.\n- HTTPS and auth.\n- Expo security guide.\n\n"
                "Internationalization\n- expo-localization.\n- RTL support.\n- Text scaling.\n\n"
                "Key Conventions\n1) Managed workflow. 2) Mobile Web Vitals. 3) expo-constants.\n"
                "4) expo-permissions. 5) expo-updates. 6) Distribution best practices.\n"
                "7) Test iOS and Android.\n\nAPI Docs: https://docs.expo.dev/"
            ),
            (
                "You are an expert in JavaScript, React Native, Expo, and Mobile UI development.\n\n"
                "Code Style and Structure:\n- Clean code.\n- Functional components with hooks.\n- Modular components.\n\n"
                "Naming:\n- camelCase variables.\n- PascalCase components.\n- hyphenated directories.\n\n"
                "JavaScript Usage:\n- Avoid globals.\n- Use ES6+.\n- PropTypes if not TS.\n\n"
                "Performance:\n- Optimize state.\n- React.memo.\n- FlatList tuning.\n- Avoid anonymous handlers.\n\n"
                "UI:\n- StyleSheet or styled-components.\n- Responsive design.\n- Fast image libs.\n\n"
                "Best Practices:\n- EAS, OTA updates.\n- Expo Router for file-based routing (https://docs.expo.dev/router/introduction/)."
            ),
        ]

    def bring_window_to_front(self) -> bool:
        windows = self.pygetwindow.getWindowsWithTitle(self.window_title) or []
        target = windows[0] if windows else None
        if target is None:
            print(f"⚠️ No se encontró una ventana con título que contenga: {self.window_title!r}")
            return False
        try:
            target.activate()
            time.sleep(0.5)
            return True
        except Exception:
            try:
                target.minimize()
                time.sleep(0.2)
                target.restore()
                time.sleep(0.5)
                return True
            except Exception:
                return False

    def setup_target_position(self) -> bool:
        print("🎯 CONFIGURACIÓN SIMPLE")
        print("=" * 30)
        print("1. Ve a Cursor y haz click en el chat")
        print(f"2. Presiona {self.capture_hotkey.upper()} para capturar posición")
        print("3. O presiona ESC para usar automático")
        print("")

        position_captured = False

        def capture_position():
            nonlocal position_captured
            self.target_position = self.pyautogui.position()
            position_captured = True
            print(f"✅ Posición: {self.target_position}")

        def use_auto():
            nonlocal position_captured
            position_captured = True
            self.target_position = None
            print("🤖 Usando automático")

        self.keyboard.add_hotkey(self.capture_hotkey, capture_position)
        self.keyboard.add_hotkey("esc", use_auto)

        try:
            while not position_captured:
                time.sleep(0.1)
        finally:
            self.keyboard.clear_all_hotkeys()

        return True

    def send_command(self, command: str) -> None:
        try:
            active_window = self.pygetwindow.getActiveWindow()
            if not active_window or "Cursor" not in (active_window.title or ""):
                if not self.bring_window_to_front():
                    print("⚠️ La ventana activa no es Cursor. Comando no enviado.")
                    return

            print(f"📝 Enviando: {command[:64]}{'...' if len(command) > 64 else ''}")

            if self.target_position:
                self.pyautogui.click(self.target_position[0], self.target_position[1])
                time.sleep(0.3)
            else:
                self.pyautogui.hotkey("ctrl", "shift", "l")
                time.sleep(0.6)

            self.pyautogui.hotkey("ctrl", "a")
            time.sleep(0.2)
            self.pyautogui.press("delete")
            time.sleep(0.2)

            self.pyautogui.typewrite(command, interval=self.key_delay_seconds)
            time.sleep(0.2)

            self.pyautogui.press("enter")
            time.sleep(0.4)

            print("✅ Enviado")

            extra_instruction = "No des guías, solo responde con código y hazlo."
            self.pyautogui.typewrite(extra_instruction, interval=self.key_delay_seconds)
            time.sleep(0.2)
            self.pyautogui.press("enter")
            time.sleep(0.2)
            print("✅ Instrucción adicional enviada")

        except Exception as exc:
            print(f"❌ Error al enviar comando: {exc}")

    def setup_hotkeys(self) -> None:
        self.keyboard.add_hotkey(self.stop_hotkey, self.stop)
        print(f"⌨️ {self.stop_hotkey.upper()} para detener")

    def stop(self) -> None:
        self.running = False
        print("🛑 Deteniendo...")

    def run_once(self) -> None:
        if not self.setup_target_position():
            return
        self.setup_hotkeys()

        print("🚀 Iniciando en 3 segundos...")
        time.sleep(3)

        try:
            for idx, command in enumerate(self.commands, 1):
                if not self.running:
                    break
                print(f"\n📝 Comando {idx}/{len(self.commands)}")
                self.send_command(command)
                if not self.running:
                    break
                print("⏳ Esperando entre comandos...")
                waited = 0.0
                while self.running and waited < self.between_commands_seconds:
                    time.sleep(0.25)
                    waited += 0.25
        except KeyboardInterrupt:
            print("\n⛔ Interrumpido")
        except Exception as exc:
            print(f"❌ Error: {exc}")
        finally:
            print("🔚 Finalizado")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple Cursor Chat Automator")
    parser.add_argument("--window-title", type=str, default="Cursor", help="Título de la ventana objetivo")
    parser.add_argument("--pause", type=float, default=0.15, help="Pausa global de pyautogui")
    parser.add_argument("--key-delay", type=float, default=0.05, help="Intervalo entre teclas al escribir")
    parser.add_argument("--between", type=float, default=5.0, help="Segundos entre comandos")
    parser.add_argument("--capture-hotkey", type=str, default="ctrl+shift+t", help="Hotkey para capturar posición")
    parser.add_argument("--stop-hotkey", type=str, default="ctrl+shift+q", help="Hotkey para detener")
    parser.add_argument(
        "--commands",
        type=str,
        nargs="*",
        default=None,
        help="Lista de comandos a enviar (si se omite, se usan los predeterminados)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    automator = SimpleCursorAutomator(
        window_title=args.window_title,
        pause_seconds=args.pause,
        key_delay_seconds=args.key_delay,
        between_commands_seconds=args.between,
        capture_hotkey=args.capture_hotkey,
        stop_hotkey=args.stop_hotkey,
        commands=args.commands,
    )
    automator.run_once()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



