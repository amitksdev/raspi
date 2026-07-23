import http.server
import socketserver
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

LOG_FILE = '/home/pi/slideshow/web_access.log'
FEH_PID_FILE = '/tmp/feh.pid'
FEH_STATE_FILE = '/tmp/feh_state'

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


def refresh_overlay():
    """Toggle info twice to force redraw"""
    send_key_to_feh("r")
    send_key_to_feh("i")
    time.sleep(2)
    send_key_to_feh("i")


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

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        if self.path == '/':
            self.path = "static/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


with ReusableTCPServer(('', 8000), MyHandler) as server:
    server.serve_forever()
