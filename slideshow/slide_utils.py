import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

LOG_FILE = "/home/pi/slideshow/web_access.log"
FEH_PID_FILE = "/tmp/feh.pid"
FEH_STATE_FILE = "/tmp/feh_state"
MASTER_LIST = "/home/pi/Pictures/Slides/feh/playlists/all_photos.txt"
ACTIVE_PLAYLIST = "/home/pi/Pictures/Slides/feh/playlists/active.txt"
DISPLAY = ":0"
XAUTHORITY = "/home/pi/.Xauthority"

Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
Path(LOG_FILE).touch(exist_ok=True)
Path(FEH_STATE_FILE).touch(exist_ok=True)


def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow()} :: {msg}\n")


def get_feh_pid():
    try:
        with open(FEH_PID_FILE, encoding="utf-8") as f:
            pid = int(f.read().strip())
        if pid > 0:
            return pid
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["pgrep", "-x", "feh"],
            capture_output=True,
            text=True,
            check=False,
        )
        pids = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if pids:
            return int(pids[0])
    except Exception:
        pass

    return None


def send_key_to_feh(key):
    """Send a key press to the active FEH window."""
    pid = get_feh_pid()
    if not pid:
        log("FEH PID not found.")
        return False

    env = os.environ.copy()
    env["DISPLAY"] = DISPLAY
    env["XAUTHORITY"] = XAUTHORITY

    try:
        result = subprocess.run(
            ["xdotool", "search", "--pid", str(pid)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        windows = [line for line in result.stdout.splitlines() if line.strip()]
        if not windows:
            log("FEH window not found.")
            return False

        wid = windows[0]
        subprocess.run(["xdotool", "windowactivate", "--sync", wid], env=env, check=False)
        subprocess.run(["xdotool", "key", "--clearmodifiers", key], env=env, check=False)
        return True

    except Exception as exc:
        log(f"Key send failed: {exc}")
        return False


def set_feh_state(state):
    with open(FEH_STATE_FILE, "w", encoding="utf-8") as f:
        f.write(state)


def toggle_pause(paused):
    set_feh_state("PAUSED" if paused else "RUNNING")
    send_key_to_feh("h")
    time.sleep(1)
    send_key_to_feh("r")


def apply_command(command):
    """Common slideshow commands shared by the Wi-Fi and MQTT drivers."""
    command = command.strip().lower()

    if command == "next":
        send_key_to_feh("n")
    elif command == "prev":
        send_key_to_feh("p")
    elif command == "pause":
        toggle_pause(True)
    elif command == "resume":
        toggle_pause(False)
    elif command == "refresh":
        send_key_to_feh("r")
    elif command in {"info", "hide_info"}:
        send_key_to_feh("i")
    else:
        return False

    return True
