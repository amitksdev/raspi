import os
import random
import shutil
import signal
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


def build_playlist(count):
    """
    Create active.txt containing the first 'count' entries from MASTER_LIST.
    count=None -> all photos
    """
    log(f"Request to build playlist: {count}")
    total = 0
    temp_file = ACTIVE_PLAYLIST + ".tmp"

    with open(MASTER_LIST, "r", encoding="utf-8") as src, open(temp_file, "w", encoding="utf-8") as dst:
        if count is None:
            shutil.copyfileobj(src, dst)
            src.seek(0)
            total = sum(1 for _ in src)
        else:
            for line in src:
                dst.write(line)
                total += 1
                if total >= count:
                    break

    pid = None
    try:
        with open(FEH_PID_FILE, encoding="utf-8") as f:
            pid = int(f.read().strip())
    except Exception:
        pass

    if pid:
        os.kill(pid, signal.SIGINT)
        time.sleep(2)

    os.replace(temp_file, ACTIVE_PLAYLIST)
    log(f"Playlist updated ({total} images)")
    return total


def build_random_playlist(count=None):
    with open(MASTER_LIST, "r", encoding="utf-8") as f:
        photos = [line.strip() for line in f if line.strip()]

    random.shuffle(photos)
    if count is not None:
        photos = photos[:count]

    tmp = ACTIVE_PLAYLIST + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(photos))
        f.write("\n")

    os.replace(tmp, ACTIVE_PLAYLIST)
    send_key_to_feh("r")


def apply_command(command):
    """Common slideshow commands shared by the Wi‑Fi and MQTT drivers."""
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
    elif command == "last10":
        build_playlist(10)
    elif command == "last100":
        build_playlist(100)
    elif command == "reset":
        build_playlist(None)
    else:
        return False

    return True
