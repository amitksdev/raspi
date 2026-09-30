import http.server
import socketserver
import time

from slide_utils import (
    apply_command,
    build_playlist,
    log,
    send_key_to_feh,
)


def refresh_overlay():
    """Toggle info twice to force redraw."""
    send_key_to_feh("r")
    send_key_to_feh("i")
    time.sleep(2)
    send_key_to_feh("i")

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode('utf-8').strip()

        log(f"Received command: {data}")

        if data.startswith("top:"):
            try:
                build_playlist(int(data.split(":", 1)[1]))
            except ValueError:
                log("Invalid top:N command")
                build_playlist(100)
        elif data in {"last10", "last100", "reset"}:
            apply_command(data)
        else:
            apply_command(data)

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
