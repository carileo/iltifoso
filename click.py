import pyautogui
import time
import pygetwindow as gw
import ctypes

pyautogui.FAILSAFE = False  # Disabilita il fail-safe (Usare con cautela!)

# Disabilita il timeout dello screensaver e la sospensione del PC
def disable_sleep():
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)  # CONTINUOUS + SYSTEM_REQUIRED

# Riabilita il comportamento normale quando lo script termina
def enable_sleep():
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # Reimposta le impostazioni predefinite

def keep_active():
    print("Lo script è attivo! Premi Ctrl+C per interrompere.")
    disable_sleep()  # Impedisce standby/sospensione

    try:
        while True:
            # Muove leggermente il mouse
            pyautogui.moveRel(1, 0, duration=0.1)
            pyautogui.moveRel(-1, 0, duration=0.1)

            # Ogni 5 minuti simula un clic su Microsoft Teams
            teams_window = None
            for window in gw.getWindowsWithTitle("Microsoft Teams"):
                if "Microsoft Teams" in window.title:
                    teams_window = window
                    break

            if teams_window:
                try:
                    teams_window.activate()  # Porta Teams in primo piano
                    time.sleep(1)  # Attendi per sicurezza
                    x, y = teams_window.left + 200, teams_window.top + 200  # Evita angoli dello schermo
                    print(f"Cliccando su Teams alle coordinate: {x}, {y}")
                    pyautogui.click(x, y)
                except Exception as e:
                    print(f"Errore durante il clic: {e}")
            else:
                print("Microsoft Teams non trovato. Attendi il prossimo tentativo...")

            time.sleep(300)  # Aspetta 5 minuti (300 secondi)

    except KeyboardInterrupt:
        print("\nInterruzione rilevata, ripristino impostazioni...")
        enable_sleep()  # Riabilita il risparmio energetico
        print("Impostazioni ripristinate. Chiusura script.")

if __name__ == "__main__":
    keep_active()
