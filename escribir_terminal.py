import pyautogui
import time

print("Coloca el cursor en el terminal de VSCode. Empieza en 5 segundos...")
time.sleep(5)

while True:
    pyautogui.typewrite("optimiza")
    pyautogui.press('enter')
    time.sleep(430)  # Espera 1 minuto

    pyautogui.typewrite("optimiza con librerias")
    pyautogui.press('enter')
    time.sleep(430)  # Espera 1 minuto

    pyautogui.typewrite("refactor")
    pyautogui.press('enter')
    time.sleep(480)  # Espera 1 minuto

    pyautogui.typewrite("codigo de produccion")
    pyautogui.press('enter')
    # Si quieres una pausa después de "codigo de produccion", descomenta la siguiente línea:
    # time.sleep(6
    # echo "Texto repetido 8"
    # echo "Texto repetido 9"
    # echo "Texto repetido 10"
    # 0)