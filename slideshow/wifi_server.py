import http.server
import os
import random
import shutil
import signal
import socketserver
import time

from slide_utils import (
    ACTIVE_PLAYLIST,
    FEH_STATE_FILE,
    MASTER_LIST,
    apply_command,
    log,
    send_key_to_feh,
)


def build_playlist(count):
    """
    Creates active.txt containing the first 'count' entries
    from MASTER_LIST.
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
        with open("/tmp/feh.pid", encoding="utf-8") as f:
            pid = int(f.read().strip())
    except Exception:
        pass

    if pid:
        os.kill(pid, signal.SIGINT)
        time.sleep(2)

    os.replace(temp_file, ACTIVE_PLAYLIST)
    log(f"Playlist updated ({total} images)")
    return total


def refresh_overlay():
    """Toggle info twice to force redraw."""
    send_key_to_feh("r")
    send_key_to_feh("i")
    time.sleep(2)
    send_key_to_feh("i")


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

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode('utf-8').strip()

        log(f"Received command: {data}")

        if data == "next":
            apply_command(data)

        elif data == "prev":
            apply_command(data)

        elif data == "pause":
            apply_command(data)

        elif data == "resume":
            apply_command(data)

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
