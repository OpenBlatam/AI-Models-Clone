from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import pyautogui
import time

from typing import Any, List, Dict, Optional
import logging
import asyncio
print("Coloca el cursor en el terminal de VSCode. Empieza en 5 segundos...")
time.sleep(5)

while True:
    pyautogui.typewrite("optimiza")
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
    pyautogui.press('enter')
    time.sleep(430)  # Espera 1 minuto

    pyautogui.typewrite("optimiza con librerias")
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
    pyautogui.press('enter')
    time.sleep(430)  # Espera 1 minuto

    pyautogui.typewrite("refactor")
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
    pyautogui.press('enter')
    time.sleep(480)  # Espera 1 minuto

    pyautogui.typewrite("codigo de produccion")
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
    pyautogui.press('enter')
    # Si quieres una pausa después de "codigo de produccion", descomenta la siguiente línea:
    # time.sleep(6
    # echo "Texto repetido 8"
    # echo "Texto repetido 9"
    # echo "Texto repetido 10"
    # 0)