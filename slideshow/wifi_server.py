import http.server
import socketserver
import os
import time
import signal
import subprocess
import random
from pathlib import Path
from datetime import datetime
import shutil


LOG_FILE = '/home/pi/slideshow/web_access.log'
#LOG_FILE = '/tmp/web_access.log'
FEH_PID_FILE = '/tmp/feh.pid'
FEH_STATE_FILE = '/tmp/feh_state'
MASTER_LIST = "/home/pi/Pictures/Slides/feh/playlists/all_photos.txt"
ACTIVE_PLAYLIST = "/home/pi/Pictures/Slides/feh/playlists/active.txt"

# Ensure files exist
Path(LOG_FILE).touch(exist_ok=True)
Path(FEH_STATE_FILE).touch(exist_ok=True)


def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.utcnow()} :: {msg}\n")


def get_feh_pid():
    try:
        with open(FEH_PID_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return None


def send_key_to_feh(key):
    """Send key press to feh window"""
    pid = get_feh_pid()
    if not pid:
        log("FEH PID not found.")
        return False

    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["XAUTHORITY"] = "/home/pi/.Xauthority"

    try:
        # Get window ID
        result = subprocess.run(
            ["xdotool", "search", "--pid", str(pid)],
            capture_output=True,
            text=True,
            env=env
        )

        wid_list = result.stdout.strip().split("\n")
        if not wid_list or wid_list[0] == "":
            log("FEH window not found.")
            return False

        wid = wid_list[0]

        # Activate window
        subprocess.run(
            ["xdotool", "windowactivate", wid],
            env=env
        )

        # Send key
        subprocess.run(
            ["xdotool", "key", key],
            env=env
        )

        return True

    except Exception as e:
        log(f"Key send failed: {e}")
        return False


def build_playlist(count):
    """
    Creates active.txt containing the first 'count' entries
    from MASTER_LIST.
    count=None -> all photos
    """
    log(f"Request to build playlist: {count}") 
    total = 0
    temp_file = ACTIVE_PLAYLIST + ".tmp"

    with open(MASTER_LIST, "r") as src, \
         open(temp_file, "w") as dst:

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

    # Restart feh
    pid = get_feh_pid()
    os.kill(pid, signal.SIGINT) 
    time.sleep(2)

    # Atomic replace
    os.replace(temp_file, ACTIVE_PLAYLIST)

    log(f"Playlist updated ({total} images)")

    # Reload feh
    # send_key_to_feh("r")

    return total

def refresh_overlay():
    """Toggle info twice to force redraw"""
    send_key_to_feh("r")
    send_key_to_feh("i")
    time.sleep(2)
    send_key_to_feh("i")

def build_random_playlist(count=None):
    with open(MASTER_LIST, "r") as f:
        photos = [line.strip() for line in f if line.strip()]

    random.shuffle(photos)

    if count is not None:
        photos = photos[:count]

    tmp = ACTIVE_PLAYLIST + ".tmp"
    with open(tmp, "w") as f:
        f.write("\n".join(photos))
        f.write("\n")

    os.replace(tmp, ACTIVE_PLAYLIST)

    send_key_to_feh("r")      # Reload feh

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode('utf-8').strip()

        log(f"Received command: {data}")

        if data == "next":
            send_key_to_feh("n")

        elif data == "prev":
            send_key_to_feh("p")

        elif data == "pause":
            with open(FEH_STATE_FILE, "w") as f:
                f.write("PAUSED")

            send_key_to_feh("h")
            time.sleep(1)
            send_key_to_feh("r")     # pause slideshow
            #refresh_overlay()        # show PAUSED

        elif data == "resume":
            with open(FEH_STATE_FILE, "w") as f:
                f.write("RUNNING")

            send_key_to_feh("h")
            time.sleep(1)
            send_key_to_feh("r")     # unpause slideshow
            #refresh_overlay()        # remove PAUSED

        elif data.startswith("top:"):
            try:
                build_playlist(int(data.split(":")[1]))
            except ValueError:
                log("Invalid top:N command")
                build_playlist(100)

        elif data == "last10":
            build_playlist(10)

        elif data == "last100":
            build_playlist(100)

        elif data == "reset":
            build_playlist(None)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Done")

    def do_GET(self):
        if self.path == '/':
            self.path = "static/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


with ReusableTCPServer(('', 8000), MyHandler) as server:
    server.serve_forever()
